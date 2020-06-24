# PyGrid Distributor for Genesis Cloud


This project is meant to automatize the distribution of a <a href="https://github.com/OpenMined/PyGrid/">
PyGrid</a> training job across multiple <a href="https://compute.genesiscloud.com">Genesis Cloud</a> 
compute instances. The training protocol is specified on a local desktop. The distributor then launches
a PyGrid distributed across multiple Genesis Cloud instances. Each instance is home to one worker node and 
one instance runs the gateway.


### How-to using a jupyter notebook:

1. <a href="https://support.genesiscloud.com/support/solutions/articles/47001101437-first-steps-connecting-to-a-linux-instance-with-gpus">
     Set up a Genesis Cloud Account</a>
1. <a href="https://account.genesiscloud.com/dashboard/security">Generate your SSH Key and Developer
     API token.</a>
1. Create a security group called <code>pygrid</code> that includes a inbound TCP connection for the 
     ports 3000 and 5000
1. Clone this repository to your local machine 

        git clone https://github.com/Benecoder/distributor.git
        cd distributor
      
1. Install the required dependencies. It is recommended to do so using your preferred virtual machine.
For compatibility down the road, make sure that you are using python version 3.7.
Here is how you would do that using anaconda.

        conda create -n pygrid_env python=3.7
        conda activate pygrid_env
        pip install -r requirements.txt

As an example a jupyter notebook is provided in <code>model.ipynb</code>.
For running the example, install jupyter lab (or notebook) and place your Genesis Cloud API token and the name of your SSH Key in environment variables.

    conda install jupyter notebook
    export GC_API_TOKEN="your-api-token"
    export GC_SSH_KEY_NAME="your-ssh-key-name"


###    Under the hood:


This is how the network is build up: Using the developer API <code>build_docker_image.py</code> creates
a new ubuntu 18 instance and installs the GPU drivers. All of the PyGrid Software that is used is 
obtained by pulling the latest docker containers and starting a redis server using docker-compose 
and the correct docker-compose file. To make sure docker, docker-compose and the correct GPU drivers 
are installed.The first instance needs to be build using the base_image_cloud_init.yml file. This 
cloud-init file makes sure the correct software is installed and once that is the case touches the
 /home/ubuntu/installation_finished file. 

On The master node it then starts a redis server based on the information in the docker-compose.yml file.
This houses one gateway node and one worker, called brutus. 

As soon as <code>main.py</code> receives the ip for the gateway it starts a additional series of workers.
These connect to the gateway using the private network between the instances.
