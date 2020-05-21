#!/bin/bash
set -eux

IS_INSTALLED=false
NVIDIA_SHORT_VERSION=430

manual_fetch_install() {
    __nvidia_full_version="430_430.50-0ubuntu2"
    for i in $(seq 1 5)
    do
      echo "Connecting to http://archive.ubuntu.com site for $i time"
      if curl -s --head  --request GET http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-"${NVIDIA_SHORT_VERSION}" | grep "HTTP/1.1" > /dev/null ;
      then
          echo "Connected to http://archive.ubuntu.com. Start downloading and installing the NVIDIA driver..."
          __tempdir="$(mktemp -d)"
          apt-get install -y --no-install-recommends "linux-headers-$(uname -r)" dkms
          wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${NVIDIA_SHORT_VERSION}/nvidia-kernel-common-${__nvidia_full_version}_amd64.deb
          wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${NVIDIA_SHORT_VERSION}/nvidia-kernel-source-${__nvidia_full_version}_amd64.deb
          wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${NVIDIA_SHORT_VERSION}/nvidia-dkms-${__nvidia_full_version}_amd64.deb
          dpkg -i "${__tempdir}"/nvidia-kernel-common-${__nvidia_full_version}_amd64.deb "${__tempdir}"/nvidia-kernel-source-${__nvidia_full_version}_amd64.deb "${__tempdir}"/nvidia-dkms-${__nvidia_full_version}_amd64.deb
          wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${NVIDIA_SHORT_VERSION}/nvidia-utils-${__nvidia_full_version}_amd64.deb
          wget -P "${__tempdir}" http://archive.ubuntu.com/ubuntu/pool/restricted/n/nvidia-graphics-drivers-${NVIDIA_SHORT_VERSION}/libnvidia-compute-${__nvidia_full_version}_amd64.deb
          dpkg -i "${__tempdir}"/nvidia-utils-${__nvidia_full_version}_amd64.deb "${__tempdir}"/libnvidia-compute-${__nvidia_full_version}_amd64.deb
          IS_INSTALLED=true
          rm -r "${__tempdir}"
          break
      fi
      sleep 2
    done
}

apt_fetch_install() {
    add-apt-repository -s -u -y restricted

    # Ubuntu has only a single version in the repository marked as "latest" of
    # this series.
    for _ in $(seq 1 5)
    do
        if apt-get install -y --no-install-recommends nvidia-utils-${NVIDIA_SHORT_VERSION} libnvidia-compute-${NVIDIA_SHORT_VERSION} \
           nvidia-kernel-common-${NVIDIA_SHORT_VERSION} \
           nvidia-kernel-source-${NVIDIA_SHORT_VERSION} \
           nvidia-dkms-${NVIDIA_SHORT_VERSION} \
           "linux-headers-$(uname -r)" dkms; then
           IS_INSTALLED=true
           break
        fi
        sleep 2
    done

}


main() {
    if grep xenial /etc/os-release; then
        manual_fetch_install
    else
       apt_fetch_install
    fi
    # remove the module if it is inserted, blacklist it
    rmmod nouveau || echo "nouveau kernel module not loaded ..."
    echo "blacklist nouveau" > /etc/modprobe.d/nouveau.conf

    # log insertion of the nvidia module
    # this should always succeed on customer instances
    if modprobe -vi nvidia; then
       nvidia-smi
       modinfo nvidia
       gpu_found=true
    else
       gpu_found=false
    fi

    if [ "${IS_INSTALLED}" = true ]; then
        echo "NVIDIA driver has been successfully installed."
    else
        echo "NVIDIA driver has NOT been installed."
    fi

    if [ "${gpu_found}" ]; then
       echo "WARNING: NVIDIA GPU device is not found or is failed"
    else
       echo "NVIDIA GPU device is found and ready"
    fi
}

main

