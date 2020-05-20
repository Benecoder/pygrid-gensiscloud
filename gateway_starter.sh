#!/bin/bash

apt-get update

set -Eeux

# enable repository including sources, update package cache

add-apt-repository -s -u restricted

VERSION=430
is_installed=false

# Ubuntu has only a single version in the repository marked as "latest" of
# this serires.
for (( i=0 ; i<5; i++ ))
do
    sudo apt install -y nvidia-utils-${VERSION} libnvidia-compute-${VERSION} \
        nvidia-kernel-common-${VERSION} \
        nvidia-kernel-source-${VERSION} \
        nvidia-dkms-${VERSION}
  sleep 2
done

# remove the module if it is inserted, blacklist it
rmmod nouveau || echo "nouveau kernel module not loaded ..."
echo "blacklist nouveau" > /etc/modprobe.d/nouveau.conf
# log insertion of the nvidia module
if modprobe nvidia ; then
   nvidia-smi
else
   echo "nvidia device not found"
fi
if [ $is_installed = true ];
then
  echo "NVIDIA driver has been successfully installed."
else
  echo "NVIDIA driver NOT been installed."
fi



# install docker
sudo apt-get --assume-yes update
sudo apt-get --assume-yes install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common


curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -


sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get --assume-yes install docker-ce docker-ce-cli containerd.io


# docker compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

cd /home/ubuntu
git clone https://github.com/Benecoder/distributor.git



