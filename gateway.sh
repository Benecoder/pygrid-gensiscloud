#!/bin/bash

# waiting for installation to finish
if [$(cloud-init status) == "running"];
then
  sleep 5
fi

touch /home/ubuntu/gateway_started.txt
