"""
Build an image that has the Nvidia Drivers, Docker and Docker-compose preinstalled.
"""
import argparse
from api_helpers import *
import time

parser = argparse.ArgumentParser(description='Build an image that has the nvidia Drivers,' +
                                             'docker and docker-compose preinstalled.')

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


def build_image_from_scratch(name):

    instance = {
        "name": name,
        "type": "vcpu-4_memory-12g_disk-80g_nvidia1080ti-1",
        "image_name": "Ubuntu 18.04",
        "ssh_key_names": [SSH_KEY],
        "security_group_names": ["standard"]
    }

    # pick the right image
    desired_image_name = 'nvidia+docker'
    available_images = get_available_images(API_TOKEN)
    if desired_image_name in [*available_images]:
        building_from_scratch = False
        instance['image_id'] = available_images[desired_image_name]
    else:
        building_from_scratch = True
        instance['image_id'] = available_images[instance['image_name']]
        with open('base_image_cloud_init.yml', 'r') as stream:
            instance['startup_script'] = stream.read()

    # pick the right ssh key
    instance['ssh_key_ids'] = get_ssh_key_ids(instance['ssh_key_names'], API_TOKEN)

    # picks the right security group
    instance['security_group_ids'] = get_security_group_ids(instance['security_group_names'], API_TOKEN)

    # create the instance
    instance['id'] = start_instance(instance, API_TOKEN)

    # waiting for the instance to start
    print('instance is starting ...')
    while get_instance_status(instance['id'], API_TOKEN) != 'active':
        time.sleep(5)

    instance['ip'] = get_instance_public_ip(instance['id'], API_TOKEN)
    print('public ip is: ' + instance['ip'])

    # waiting for the installation to finish
    if building_from_scratch:
        print('installing nvidia drivers and docker ...')
        while get_startup_script_status(instance['ip']) != 'done':
            time.sleep(5)

        # creating the image snapshot
        snapshot_id = create_instance_snapshot(instance['id'], desired_image_name, API_TOKEN)

        while get_snapshot_status(snapshot_id, API_TOKEN) != 'active':
            time.sleep(5)

    return instance


if __name__ == '__main__':
    args = parser.parse_args()
    API_TOKEN = args.api_token
    SSH_KEY = args.ssh_key

    build_image_from_scratch('gateway')
