import yaml
import argparse
import os
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

        self.path_to_dc_file = self.compose_docker()
        self.ip = self.create_instance()

    def compose_docker(self):

        environment = ['GRID_NETWORK_URL=http://'+self.gateway_ip+':'+str(self.gateway_port),
                       'ID='+self.name,
                       'ADDRESS=http://localhost:'+self.port,
                       'PORT='+self.port]

        with open('docker-compose-node-form.yml', 'r') as stream:
            form = yaml.safe_load(stream)

        node_service = {'image': form['services']['name']['image'],
                        'environment': environment,
                        'depends_on': form['services']['name']['depends_on'],
                        'ports': form['services']['name']['ports']}
        services = {'redis': form['services']['redis'],
                    self.name: node_service}
        configuration = {'version': form['version'],
                         'services': services}

        path_to_dc_file = 'docker-compose-'+self.name+'.yml'
        with open(path_to_dc_file, 'w') as stream:
            yaml.dump(configuration, stream)

        return path_to_dc_file

    def create_instance(self):

        # assemble th startup script
        with open('node_starter.sh', 'r') as stream:
            startup_script = stream.readlines()

        startup_script[2] = 'GATEWAYIP='+self.gateway_ip+'\n'
        startup_script[3] = 'DOCKER_PATH='+os.path.abspath(self.path_to_dc_file)+'\n'
        startup_script = ''.join(startup_script)

        # assemble the parameters
        instance = {
            "name": self.name,
            "type": "vcpu-4_memory-12g_disk-80g_nvidia1080ti-1",
            "image_name": "docker+nvidia",
            "ssh_key_names": [SSH_KEY],
            "security_group_names": ["standard"],
            "startup_script": startup_script,
        }

        # pick the right image
        instance['image_id'] = get_image_id(instance['image_name'], API_TOKEN)

        # pick the right ssh key
        instance['ssh_key_ids'] = get_ssh_key_ids(instance['ssh_key_names'], API_TOKEN)

        instance['security_group_ids'] = get_security_group_ids(instance['security_group_names'], API_TOKEN)

        # create the instance
        instance['id'] = start_instance(instance, API_TOKEN)

        while get_instance_status(instance['id'], API_TOKEN) != 'active':
            time.sleep(10)
        
        ip = get_instance_public_ip(instance['id'], API_TOKEN)
        print('public ip is: '+ip)
        return ip


if __name__ == '__main__':

    args = parser.parse_args()
    API_TOKEN = args.api_token
    SSH_KEY = args.ssh_key

    test_node = Node('hans-joachim', '192.162.10.21')
