<h1>
    PyGrid Distributor for Genesis Cloud
</h1>
<p>
    This project is meant ot automatize the distribution of a <a href="https://github.com/OpenMined/PyGrid/">
    PyGrid</a> training job across multiple <a href="https://compute.genesiscloud.com">Genesis Cloud</a> 
    compute instances. The training protocol is specified on a local desktop. The distributor then launches
    a PyGrid distributed across multiple Genesis Cloud instances. Each instance is home to one worker node and 
    one instance runs the gateway.
</p>

<h3>
    How-to:
</h3>
<ol>
    <li><a href="https://support.genesiscloud.com/support/solutions/articles/47001101437-first-steps-connecting-to-a-linux-instance-with-gpus">
     Set up a Genesis Cloud Account</a></li>
    <li><a href="https://account.genesiscloud.com/dashboard/security">Generate your SSH Key and Developer
     API token.</a></li>
     <li>Clone this repository to your local machine
     <pre><code>git clone https://github.com/Benecoder/distributor.git<br>cd distributor</code></pre>
     </li>
     <li> All installations in the cloud are performed once and then saved in a snapshot called 
     <code>nvidia+docker</code> Building this image for the first time might take a few minutes.
     To start the gateway
     <pre><code>python main.py --api_token="your API token" --ssh_key="your ssh key"</code></pre></li>
</ol>
