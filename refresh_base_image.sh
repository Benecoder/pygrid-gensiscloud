#!/bin/bash
# run when launching from a saved nvidia+docker snapshot

cd /home/ubuntu/pygrid-gensiscloud
git pull

cd /home/ubuntu/pygrid-gensiscloud
docker pull openmined/grid-gateway:latest
docker pull openmined/grid-node:latest

touch /home/ubuntu/refresh_finished.txt

docker-compose -f /home/ubuntu/distributor/docker-compose.yml up