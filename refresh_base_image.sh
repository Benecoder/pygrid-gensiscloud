#!/bin/bash
# run when launching from a saved nvidia+docker snapshot

cd /home/ubuntu/distributor
git pull

cd /home/ubuntu/distributor
docker pull openmined/grid-gateway:latest
docker pull openmined/grid-node:latest
docker-compose -f /home/ubuntu/distributor/docker-compose.yml up