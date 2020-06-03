<h1>
    PyGrid Distributor for Genesis Cloud
</h1>
<p>
    This project is meant to automatize the distribution of a <a href="https://github.com/OpenMined/PyGrid/">
    PyGrid</a> training job across multiple <a href="https://compute.genesiscloud.com">Genesis Cloud</a> 
    compute instances. The training protocol is specified on a local desktop. The distributor then launches
    a PyGrid distributed across multiple Genesis Cloud instances. Each instance is home to one worker node and 
    one instance runs the gateway.
</p>

<h3>
    How-to using a jupyter notebook:
</h3>
<ol>
    <li><a href="https://support.genesiscloud.com/support/solutions/articles/47001101437-first-steps-connecting-to-a-linux-instance-with-gpus">
     Set up a Genesis Cloud Account</a></li>
    <li><a href="https://account.genesiscloud.com/dashboard/security">Generate your SSH Key and Developer
     API token.</a></li>
     <li>Create a security group called <code>pygrid</code> that includes a inbound TCP connection for the 
     ports 3000 and 5000</li>
     <li>Clone this repository to your local machine
     <pre><code>git clone https://github.com/Benecoder/distributor.git; cd distributor</code></pre>
     </li>
     <li><a href="https://github.com/OpenMined/PySyft">Install PySyft and start jupyter lab</a>. An example is posted in
     <code>model.ipynb</code>. For running the example, place your Genesis Cloud API token and the name of your SSH Key in environment variables.
<pre>export GC_API_TOKEN="your-api-token"
export GC_SSH_KEY_NAME="your-ssh-key-name"</pre></li>
</ol>

<h3>
    Under the hood:
</h3>
<p>
    This is how the network is build up: Using the developer API <code>build_docker_image.py</code> creates
    a new ubuntu 18 instance and installs the GPU drivers. All of the PyGrid Software that is used is 
    obtained by pulling the latest docker containers and starting a redis server using docker-compose 
    and the correct docker-compose file. To make sure docker, docker-compose and the correct GPU drivers 
    are installed.The first instance needs to be build using the base_image_cloud_init.yml file. This 
    cloud-init file makes sure the correct software is installed and once that is the case touches the
     /home/ubuntu/installation_finished file.
</p>
<p>
   On The master node it then starts a redis server based on the information in the docker-compose.yml file.
   This houses one gateway node and one worker, called brutus.  
</p>
<p>
    As soon as <code>main.py</code> receives the ip for the gateway it starts a additional series of workers.
    These connect to the gateway using the private network between the instances.
</p>