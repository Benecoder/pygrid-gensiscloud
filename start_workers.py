import argparse
from api_helpers import *
import time
import random
import string

parser = argparse.ArgumentParser(description="Building a PyGrid across Genesis Cloud instances.")


parser.add_argument(
    "--gateway_ip",
    type=str, required=True,
    help="The private IPv4 of the gateway. The gateway needs to be starting the workers."
)

parser.add_argument(
    "--api_token",
    type=str, required=True,
    help="The API token. Generate a new one under https://account.genesiscloud.com/dashboard/security."
)

parser.add_argument(
    "--ssh_key",
    type=str, required=True,
    help="The name of your ssh key. Public key needs to be stored here (" +
         "https://account.genesiscloud.com/dashboard/security) and private key in ~/.ssh/id_rsa ."
)

parser.add_argument(
    "--workers",
    type=int, default=1,
    help="The number of worker instances to be launched"
)


class Node:

    def __init__(self,  name, gateway_ip, api_token, ssh_key, gateway_port=None, port=None):

        self.name = name
        self.gateway_ip = gateway_ip
        self.api_token = api_token
        self.ssh_key = ssh_key

        if gateway_port is None:
            self.gateway_port = '5000'
        else:
            self.gateway_port = gateway_port

        if port is None:
            self.port = '3000'
        else:
            self.port = port

        self.ip = self.create_instance()

    def create_instance(self):

        # assemble th startup script
        with open('node_starter.sh', 'r') as stream:
            startup_script = stream.readlines()

        startup_script[2] = 'GATEWAYIP='+self.gateway_ip+'\n'
        startup_script[4] = 'NAME='+self.name
        startup_script = ''.join(startup_script)

        # assemble the parameters
        instance = {
            "name": self.name,
            "type": "vcpu-4_memory-12g_disk-80g_nvidia1080ti-1",
            "image_name": "nvidia+docker",
            "ssh_key_names": [self.ssh_key],
            "security_group_names": ["standard"],
            "startup_script": startup_script,
        }

        # pick the right image
        avail_images = get_available_images(self.api_token)
        instance['image_id'] = avail_images[instance['image_name']]

        # pick the right ssh key
        instance['ssh_key_ids'] = get_ssh_key_ids(instance['ssh_key_names'], self.api_token)

        instance['security_group_ids'] = get_security_group_ids(instance['security_group_names'], self.api_token)

        # create the instance
        instance['id'] = start_instance(instance, self.api_token)

        print('instance is starting ...')
        while get_instance_status(instance['id'], self.api_token) != 'active':
            time.sleep(10)
        time.sleep(10)

        ip = get_instance_public_ip(instance['id'], self.api_token)
        print('public ip is: '+ip)

        print('running startup script ...')
        error_count = 0
        installation_finished = False
        while not installation_finished:
            time.sleep(5)
            status = get_startup_script_status(ip)
            installation_finished = (status == '/home/ubuntu/installation_finished')
            if not installation_finished and status.split(':')[0] != 'ls':
                error_count += 1
            if error_count > 5:
                print('checking the cloud-init status failed for the fifth time.')
                print('Unable to determine state of the instance.')
                print('exiting...')
                exit()

        return ip


def random_string(n):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(n))


def get_list_of_names(n_o_names):
    name_repo = ['Alice', 'Bob', 'Carlos', 'Eve', 'Frank', 'Grace',
                 'Judy', 'Hans', 'Heidi', 'Mike', 'Ted', 'Wendy']
    if len(name_repo) > n_o_names:
        return name_repo[:n_o_names]
    else:
        random_names = [random_string(7) for _ in range(n_o_names-len(name_repo))]
        return name_repo+random_names


def start_workers(gateway_ip, api_token, ssh_key, no_workers=1):

    names = get_list_of_names(no_workers)
    if no_workers == 1:
        print('Launching ' + names[0] + ' as a worker node on a separate instance.')
    else:
        print('Launching ' + ', '.join(names[:-1]) + ' and ' + names[-1] + ' as worker nodes ' +
              ' on separate instances.')

    nodes = [Node(name, gateway_ip, api_token, ssh_key) for name in names]

    return nodes


if __name__ == '__main__':
    args = parser.parse_args()
    start_workers(args.gateway_ip, args.api_token, args.ssh_key, args.workers)
