import sys
import syft as sy
import torch
from syft.workers.node_client import NodeClient

hook = sy.TorchHook(torch)

grid = sy.PublicGridNetwork(hook,'http://'+sys.argv[1]+':5000')


bob = NodeClient(hook,'ws://'+sys.argv[1]+':3000')


a = torch.tensor([1,2,3,5])
a.send(bob)


