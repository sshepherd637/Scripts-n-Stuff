#!/usr/bin/env python3

###########################
# Created by Sam Shepherd #
#   Checks all nodes and  #
#   sorts successful and  #
#       failed nodes.     #
#       12/12/2021        #
###########################

# Import required modules to operate this task
import os, sys
import glob
from aiida import load_profile
from aiida.orm import load_node
from aiida.common.exceptions import NotExistent

# load my profile
load_profile('samshepherd')

os.mkdir(os.path.join(os.getcwd(), 'FAILS'))

# Easiest to specify the general form of the labels using the sys.argv command.
DirsGen = f'{sys.argv[1]}*' 
extension = f'_{sys.argv[2]}'

# Can check for the current labels we need using glob and a for loop.
Dirs = glob.glob(DirsGen)

# with the individual directories, we are going to create a dictionary of labels using the extension.
labelsDir = {}
for dir in Dirs:
    label = dir + extension
    try:
        node = load_node(label)
        if node.is_finished == True:
            labelsDir[label] = 'Finished'
        else: 
            labelsDir[label] = 'Failed'
            
    except NotExistent:
        print(f"""No Node found for label {label}""")
        labelsDir[label] = 'Not Found'

# Write a log file so we can check whether a directory has passed or failed, if it has passed, leave it be, if failed, move to the failed dir
counter = 0
with open('log.file', 'w+') as logfile:
    for item in labelsDir.items():
        line = f'{item[0]} : {item[1]}'
        logfile.writelines(f'{line}\n')
        if item[1] != 'Finished':
            initPath = os.path.join(os.getcwd(), '_'.join(item[0].split('_')[:2]))
            finPath = os.path.join(os.getcwd(), 'FAILS', '_'.join(item[0].split('_')[:2]))
            os.rename(initPath, finPath)
            counter += 1

# because the failures are now handled slightly differently, if the directory 'FAILS' is empty, delete it.
if len(os.listdir(os.path.join(os.getcwd(), 'FAILS'))) == 0:
    os.rmdir(os.path.join(os.getcwd(), 'FAILS'))

# handle everything else here
print(f"""Statistics for the current directory:
Successful Calculations = {len(Dirs) - counter}
Failed Calculations = {counter}""")


