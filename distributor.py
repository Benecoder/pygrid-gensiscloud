import argparse
from api_helpers import *
import time


parser = argparse.ArgumentParser(description="Building a PyGrid across Genesis Cloud instances.")

parser.add_argument(
    "--api_token",
    type=str,
    help="The API token. Generate a new one under https://account.genesiscloud.com/dashboard/security."
)

parser.add_argument(
    "--ssh_key",
    type=str,
    help="The name of your ssh key. Public key needs to be stored here (" +
         "https://account.genesiscloud.com/dashboard/security) and private key in ~/.ssh/id_rsa ."
)


class Node:

    def __init__(self,  name, gateway_ip, gateway_port=None, port=None):

        self.name = name
        self.gateway_ip = gateway_ip

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
            "ssh_key_names": [SSH_KEY],
            "security_group_names": ["standard"],
            "startup_script": startup_script,
        }

        # pick the right image
        avail_images = get_available_images(API_TOKEN)
        instance['image_id'] = avail_images[instance['image_name']]

        # pick the right ssh key
        instance['ssh_key_ids'] = get_ssh_key_ids(instance['ssh_key_names'], API_TOKEN)

        instance['security_group_ids'] = get_security_group_ids(instance['security_group_names'], API_TOKEN)

        # create the instance
        instance['id'] = start_instance(instance, API_TOKEN)

        print('instance is starting ...')
        while get_instance_status(instance['id'], API_TOKEN) != 'active':
            time.sleep(10)
        
        ip = get_instance_public_ip(instance['id'], API_TOKEN)
        print('public ip is: '+ip)

        print('running startup script ...')
        while get_startup_script_status(ip) != 'done':
            time.sleep(10)

        return ip


if __name__ == '__main__':

    args = parser.parse_args()
    API_TOKEN = args.api_token
    SSH_KEY = args.ssh_key

    test_node = Node('peter', '192.162.10.21')
