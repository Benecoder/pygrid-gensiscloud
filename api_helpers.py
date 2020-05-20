import requests
import json
import subprocess


def get_available_images(API_TOKEN):
    # getting a list of available instance images.

    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    # You can set the type parameter to get only images of a specific type, e.g. 'base-os' or 'snapshot'.
    params = {
        # 'type':'base-os',
        "per_page": 50,
        "page": 1,
    }
    response = requests.get(
        "https://api.genesiscloud.com/compute/v1/images", headers=headers, params=params
    )

    if response.status_code != 200:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()

    available_images = {}
    for image in response.json()["images"]:
        available_images[image["name"]] = image["id"]

    return available_images


def get_ssh_key_ids(ssh_key_names, API_TOKEN):
    # getting a list of available SSH Keys and looking up the ID

    # Setting the secret auth token and content type in the headers of all API calls
    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    params = {"per_page": 50, "page": 1}
    response = requests.get(
        "https://api.genesiscloud.com/compute/v1/ssh-keys",
        headers=headers,
        params=params,
    )

    if response.status_code != 200:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()

    available_ssh_keys = {}
    for ssh_key in response.json()["ssh_keys"]:
        available_ssh_keys[ssh_key["name"]] = ssh_key["id"]

    ssh_key_ids = []
    for ssh_key_name in ssh_key_names:
        ssh_key_ids.append(available_ssh_keys[ssh_key_name])

    return ssh_key_ids


def get_security_group_ids(security_group_names, API_TOKEN):
    # getting a list of security groups and the id of a specifc security group

    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    params = {"per_page": 50, "page": 1}
    response = requests.get(
        "https://api.genesiscloud.com/compute/v1/security-groups",
        headers=headers,
        params=params,
    )

    if response.status_code != 200:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()

    available_security_groups = {}
    for security_group in response.json()["security_groups"]:
        available_security_groups[security_group["name"]] = security_group["id"]

    security_group_ids = []

    for security_group_name in security_group_names:
        security_group_ids.append(available_security_groups[security_group_name])

    return security_group_ids


def start_instance(instance, API_TOKEN):
    # Creating an instance

    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    jsonbody = {
        "name": instance["name"],
        "hostname": instance["name"],
        "type": instance["type"],
        "image": instance["image_id"],
        "ssh_keys": instance["ssh_key_ids"],
        "security_groups": instance["security_group_ids"]}
    if 'startup_script' in [*instance]:
        jsonbody['metadata'] = {"startup_script": instance["startup_script"]}

    response = requests.post(
        "https://api.genesiscloud.com/compute/v1/instances",
        headers=headers,
        json=jsonbody,
    )

    if response.status_code != 201:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()

    instance_id = response.json()["instance"]["id"]
    print("Creating instance " + instance_id)
    return instance_id


def get_instance_status(instance_id, API_TOKEN):

    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    response = requests.get(
        "https://api.genesiscloud.com/compute/v1/instances/" + instance_id,
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()["instance"]["status"]
    else:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()


def get_instance_public_ip(instance_id, API_TOKEN):

    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    response = requests.get(
        "https://api.genesiscloud.com/compute/v1/instances/" + instance_id,
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()["instance"]["public_ip"]
    else:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()


def get_startup_script_status(public_ip):

    command = ['ssh', 'ubuntu@'+public_ip,
               '-o', 'StrictHostKeyChecking=no',
               'cloud-init status']

    output = subprocess.run(command, capture_output=True)
    if output.returncode == 0:
        return output.stdout[:-1].decode('utf-8').split(' ')[-1]
    else:
        print('Determining the cloud-init status failed.')
        print('return code: '+str(output.returncode))
        exit()


def create_instance_snapshot(instance_id, snapshot_name, API_TOKEN):

    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    jsonbody = {
        "name": snapshot_name,
    }
    response = requests.post(
        "https://api.genesiscloud.com/compute/v1/instances/"
        + instance_id
        + "/snapshots",
        headers=headers,
        json=jsonbody,
    )

    if response.status_code != 201:
        print(response.status_code)
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        exit()

    snapshot_id = response.json()["snapshot"]["id"]
    print("Creating snapshot " + snapshot_id + " of instance " + instance_id)
    return snapshot_id


def get_snapshot_status(snapshot_id, API_TOKEN):
    headers = {"Content-Type": "application/json", "X-Auth-Token": API_TOKEN}
    response = requests.get(
        "https://api.genesiscloud.com/compute/v1/snapshots/" + snapshot_id,
        headers=headers,
    )

    if response.status_code == 200:
        return response.json()['snapshot']['status']
    else:
        return 'instance unavailable'
