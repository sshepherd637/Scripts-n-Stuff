#!/Users/samshepherd/envs/AiiDA_env/bin/python3

# A quick script to convert a file with the pks of a group of nodes ( as output by verdi process list ) to a file with their labels.

import os
from aiida.orm import load_node
from aiida import load_profile

# specify the profile we are working within. 
load_profile('samshepherd')

# specify the node file path
node_file = os.path.join(os.getcwd(), 'nodes')

# open it for the pks
with open(node_file, 'r') as handle:
	data = handle.readlines()

# open the label file to write to
new_file = open('labels', 'w+')

# iterate over all lines
for i in range(len(data)):
	pk = data[i].split()[0]
	node = load_node(pk)
	label = node.label
	new_file.writelines(f'{label}\n')