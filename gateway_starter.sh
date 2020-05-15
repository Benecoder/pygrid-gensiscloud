#!/bin/bash

# install graphic card drivers
set -eux
__nvidia_full_version="430_430.50-0ubuntu2"
__nvidia_short_version="430"
is_installed=false
for i in $(seq 1 5)
do
  echo "Connecting to http://archive.ubuntu.com site for $i time"
  if curl -s --head --fail --request GET http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${__nvidia_short_version} ;
  then
      echo "Connected to http://archive.ubuntu.com. Start downloading and installing the NVIDIA driver..."
      __tempdir="$(mktemp -d)"
      apt-get install -y --no-install-recommends "linux-headers-$(uname -r)" dkms
      wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${__nvidia_short_version}/nvidia-kernel-common-${__nvidia_full_version}_amd64.deb
      wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${__nvidia_short_version}/nvidia-kernel-source-${__nvidia_full_version}_amd64.deb
      wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${__nvidia_short_version}/nvidia-dkms-${__nvidia_full_version}_amd64.deb
      dpkg -i "${__tempdir}"/nvidia-kernel-common-${__nvidia_full_version}_amd64.deb "${__tempdir}"/nvidia-kernel-source-${__nvidia_full_version}_amd64.deb "${__tempdir}"/nvidia-dkms-${__nvidia_full_version}_amd64.deb
      wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${__nvidia_short_version}/nvidia-utils-${__nvidia_full_version}_amd64.deb
      wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${__nvidia_short_version}/libnvidia-compute-${__nvidia_full_version}_amd64.deb
      dpkg -i "${__tempdir}"/nvidia-utils-${__nvidia_full_version}_amd64.deb "${__tempdir}"/libnvidia-compute-${__nvidia_full_version}_amd64.deb
      rmmod nouveau
      modprobe nvidia
      nvidia-smi
      is_installed=true
      rm -r "${__tempdir}"
      break
  fi
  sleep 2
done
if [ $is_installed = true ];
then
  echo "NVIDIA driver has been installed."
else
  echo "NVIDIA driver has NOT been installed. Because we can NOT reach to http://archive.ubuntu.com site which hosted necessary deb packages for installation."
fi



# install docker
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


sudo apt-get --assume-yes update
sudo apt-get --assume-yes install docker-ce docker-ce-cli containerd.io


# docker compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose


