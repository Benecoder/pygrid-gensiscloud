#!/bin/bash

GATEWAYIP=
NODEIP=$(hostname -I | awk '{print $1}')
NAME=

echo "
version: '3'
services:
    redis:
        image: redis:latest
        expose:
        - 6379
        ports:
        - 6379:6379
    $NAME:
        image: openmined/grid-node:dev
        environment:
                - GRID_NETWORK_URL=http://$GATEWAYIP:5000
                - ID=$NAME
                - ADDRESS=http://$NODEIP:3000/
                - PORT=3000
        depends_on:
                - "redis"
        ports:
        - 3000:3000" >> /home/ubuntu/docker-compose.yml

docker pull opemnined/grid-gateway:dev

docker-compose up