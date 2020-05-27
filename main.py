from build_docker_image import *
from start_workers import *
import argparse

parser = argparse.ArgumentParser(description='Launches the PyGrid on multiple Instances.')

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

parser.add_argument(
    "--workers",
    type=int, default=1,
    help="The number of worker instances to be launched"
)


if __name__ == '__main__':
    args = parser.parse_args()
    api_token = args.api_token
    ssh_key = args.ssh_key
    no_workers = args.workers

    build_image('gateway', ssh_key, api_token)
    start_workers(api_token, ssh_key, no_workers)
