"""
Build an image that has the Nvidia Drivers, Docker and Docker-compose preinstalled.
"""
import argparse
import time
import subprocess
import string
import random
from genesiscloud.client import Client, INSTANCE_TYPES

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


def check_for_file(public_ip, file_name):

    command = ['ssh', 'ubuntu@'+public_ip,
               '-o', 'StrictHostKeyChecking=accept-new',
               '-o', 'ConnectTimeout=50 ',
               'ls ' + file_name]

    error_count = 0
    while error_count < 6:
        output = subprocess.run(command, capture_output=True)
        stdout = output.stdout[:-1].decode('utf-8')
        stder = output.stderr[:-1].decode('utf-8')

        if stdout:
            # success
            return True
        elif stder.split(':')[0] == 'ls':
            # ssh call succeeded, but file missing
            return False

        error_count += 1
        time.sleep(5)

    print('Checking for the presence of the confirmation file failed.')
    exit()


def wait_for_file(ip, filename):
    while not check_for_file(ip, filename):
        time.sleep(5)


def create_gateway(client, ssh_key_name, name='gateway'):
    """
    Creates the Gateway node of the Network. Makes sure the Nvidia GPU
    drivers and docker are installed. If that is the case it saves the
    image in a snapshot.

    :param client: A instance of the pygc Client class
    :param ssh_key_name: name of the ssh key
    :param name: name of the gateway
    :return: Instance dictionary, as returned by pygc Client.Instances.get()
    """

    # pick the right image and startup script
    snapshot_list = list(client.Snapshots.find({'name': 'nvidia+docker'}))
    if snapshot_list:
        from_scratch = False
        image = snapshot_list[0]
        with open('refresh_base_image.sh', 'r') as stream:
            startup_script = stream.read()
        print('Using the prebuild snapshot with docker installed.')
    else:
        from_scratch = True
        image = list(client.Images.find({"name": 'Ubuntu 18.04'}))[0]
        with open('base_image_cloud_init.yml', 'r') as stream:
            startup_script = stream.read()
        print('Building a image where docker is newly installed.')

    # pick the right ssh key
    sshkey = list(client.SSHKeys.find({"name": ssh_key_name}))[0]

    # pick the right instance type
    instance_type = list(INSTANCE_TYPES.keys())[0]

    # pick the right security groups
    security_groups = [next(client.SecurityGroups.find({'name': key})).id for key in ['standard', 'pygrid']]

    # create the instance
    instance = client.Instances.create(name=name,
                                       hostname=name,
                                       ssh_keys=[sshkey.id],
                                       security_groups=security_groups,
                                       image=image.id,
                                       type=instance_type,
                                       metadata={"startup_script":
                                                 startup_script})

    # wait for it to become active
    print('Instance '+str(instance.id)+' is starting.')
    while instance.status != 'active':
        time.sleep(5)
        instance = client.Instances.get(instance.id)
        print(f"{instance.status}\r", end="")
    time.sleep(5)

    print('instance is active at '+str(instance.public_ip))

    # wait for the startup script to finish
    if from_scratch:
        wait_for_file(instance.public_ip, '/home/ubuntu/build_finished.txt')
        snapshot = client.Snapshots.create(name='nvidia+docker',
                                           instance_id=instance.id)
        while snapshot.status == 'creating':
            time.sleep(5)
            snapshot = client.Snapshots.get(snapshot.id)
    else:
        wait_for_file(instance.public_ip, '/home/ubuntu/refresh_finished.txt')

    return instance


def create_worker(client, ssh_key_name, gateway_ip, name):
    """
    Creates A worker node based on the nvidia+docker snapshot.
    :param client: A instance of the pygc client class
    :param ssh_key_name: name of the ssh key
    :param gateway_ip: ip of the gateway
    :param name: name of the worker
    :return: Instance dictionary, as returned by pygc Client.Instances.get()
    """
    # pick the right image
    image = list(client.Snapshots.find({'name': 'nvidia+docker'}))[0]

    # collect the startup script
    # assemble th startup script
    with open('node_starter.sh', 'r') as stream:
        startup_script = stream.readlines()

    startup_script[2] = 'GATEWAYIP=' + gateway_ip + '\n'
    startup_script[4] = 'NAME=' + name
    startup_script = ''.join(startup_script)

    # pick the right ssh key
    sshkey = list(client.SSHKeys.find({"name": ssh_key_name}))[0]

    # pick the right security groups
    security_groups = [next(client.SecurityGroups.find({'name': key})).id for key in ['standard', 'pygrid']]

    # pick the right instance type
    instance_type = list(INSTANCE_TYPES.keys())[0]

    # create the instance
    instance = client.Instances.create(name=name,
                                       hostname=name,
                                       ssh_keys=[sshkey.id],
                                       security_groups=security_groups,
                                       image=image.id,
                                       type=instance_type,
                                       metadata={"startup_script":
                                                 startup_script})

    # wait for it to become active
    print('Worker '+name+'('+str(instance.id)+') is starting.')
    while instance.status != 'active':
        time.sleep(5)
        instance = client.Instances.get(instance.id)
        print(f"{instance.status}\r", end="")
    time.sleep(5)

    # wait for the startup script to finish
    wait_for_file(instance.public_ip, '/home/ubuntu/worker_ready.txt')

    return instance


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


def create_workers(client, ssh_key_name, gateway_ip, no_workers=1):

    names = get_list_of_names(no_workers)
    if no_workers == 1:
        print('Launching ' + names[0] + ' as a worker node on a separate instance.')
    else:
        print('Launching ' + ', '.join(names[:-1]) + ' and ' + names[-1] + ' as worker nodes ' +
              ' on separate instances.')

    nodes = [create_worker(client, ssh_key_name, gateway_ip, name) for name in names]

    return nodes


if __name__ == '__main__':
    args = parser.parse_args()
    api_token_arg = args.api_token
    ssh_key_arg = args.ssh_key

    my_client = Client(api_token_arg)
    if not my_client.connect():
        exit()

    gateway = create_gateway(my_client, ssh_key_arg)
    create_workers(my_client, ssh_key_arg, gateway.private_ip)
