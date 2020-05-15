#!/bin/bash

GATEWAYIP=
DOCKER_PATH=

sudo docker pull openmined/grid-node

scp ubuntu@$GATEWAYIP:$DOCKER_PATH.yml docker-compose.yml

sudo docker-compose up