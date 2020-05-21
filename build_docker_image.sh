#!/bin/bash

set -Eeux

# enable repository including sources, update package cache

add-apt-repository -s -u restricted

VERSION=430
is_installed=false

# Ubuntu has only a single version in the repository marked as "latest" of
# this serires.
for (( i=0 ; i<5; i++ ))
do
    apt install -y nvidia-utils-${VERSION} libnvidia-compute-${VERSION} \
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

