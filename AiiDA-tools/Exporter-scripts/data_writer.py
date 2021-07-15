#!/usr/bin/env python3
# Script to write all of the desired calculation files to a single output datafile tracked using data tracking

# import the modules we need
import os, sys
from re import L
import glob
from typing import List
import aiida
from aiida.orm import load_node, SinglefileData, Str
from aiida.engine import calcfunction
from aiida.orm.nodes import data
from aiida.plugins import DataFactory
import numpy as np
import argparse

# loading the aiidav profile
aiida.load_profile('samshepherd')

# load the list data function
ListData = DataFactory('list')

# load the command line arguments to the script 
parser = argparse.ArgumentParser(description='Provenance tracking combination script for all datafiles')
parser.add_argument('dirs', metavar='directories', type=str, help='general directory name')
parser.add_argument('--add', metavar='additional text', type=str, help='additional text to help identify labels')
parser.add_argument('--out', metavar='output node label', type=str, help='identifier label for output data file')
parser.add_argument('--eV', help='output the results in units of eV', action='store_true')
parser.add_argument('--AU', help='output the results in atomic units')

args = parser.parse_args()
dir_general = args.dirs + '*'

# With dir_names created, we now want to loop into every directory with the associated directory name using glob
dir_paths = os.path.join(os.getcwd(), dir_general)
dir_names = glob.glob(dir_paths)
parent_wd = os.getcwd()

# helpful little function 
def listtostring(list):
    str1 = ' '
    return str1.join(list)

# Now we can loop using the list of directory names within the paths, this must be within a function
# to save the data provenance

def DatafileGetter(l):
    """ Non tracked function to operate all looping within the directory paths and provide all lists to the writter function"""
    lists = [[], [], [], []]
    for i in l: # get list gets the object content as a list, need to refer to one list hence [0]
        label = os.path.basename(i)
        lists[0].append(label)
        frame_handle = label + '.xyz'
        if args.add != None:
            label += args.add
        node = load_node(label)
        os.chdir(i)
        file_path = os.path.join(os.getcwd(), frame_handle)
        lists[1].append(node.outputs.atomic_forces.pk)
        lists[2].append(node.outputs.output_parameters.pk)
        lists[3].append(file_path)
    return lists
        
@calcfunction
def DatafileWriter(framename, arraynode, dictnode, frame):
    """ This is the writer function that stores all provenance within the writing of the overall datafile"""
    name = framename.value
    frame_content = frame.get_content().splitlines()
    atomic_forces = np.array(arraynode.get_array('forces')[1:, 2:])
    energy_value = dictnode.attributes['energy']
    x_force, y_force, z_force = atomic_forces[:,0], atomic_forces[:,1], atomic_forces[:,2]
    
    if args.eV == True:
        energy_value *= 27.211396641308
        x_force = [float(i) * 51.422067 for i in x_force]
        y_force = [float(i) * 51.422067 for i in y_force]
        z_force = [float(i) * 51.422067 for i in z_force]
    

    for j in range(len(frame_content)):
        if j == 0: 
            datafile.writelines(f'{frame_content[j]}\n')
        elif j == 1:
            lattice_line = frame_content[j].split()
            lattice_line[-4] = 'energy=' + str(energy_value)
            datafile.writelines(f'{listtostring(lattice_line)}\n')
        elif j >= 2 and j <= (len(frame_content)):
            atom_line = frame_content[j].split()[:4]
            atom_line.append('%.9f'%(float(x_force[j-2])))
            atom_line.append('%.9f'%(float(y_force[j-2])))
            atom_line.append('%.9f'%(float(z_force[j-2])))
            atom_str = '{0[0]:<2}{0[1]:>14}{0[2]:>14}{0[3]:>14}{0[4]:>20}{0[5]:>20}{0[6]:>20}'.format(atom_line)
            datafile.writelines(f'{atom_str}\n')


# With both functions now created we can loop over our main function, naming all output lists and producing variable names

# call the first function to get all list names etc...
lists = DatafileGetter(dir_names)

# change back to parent dir to store datafile
os.chdir(parent_wd)
FrameNames, ArrayNodes, DictNodes, FrameData = lists[0], lists[1], lists[2], lists[3]

# takes care of units using the additional command line arguments
if args.eV == True:
    datafile_label = 'Datafile_eV.xyz'
else:
    datafile_label = 'Datafile_AU.xyz'
datafile = open(datafile_label, 'w+')
tmp_path = os.path.join(os.getcwd(), datafile_label)

# complete the looping for all files within FrameNames
for i in range(len(FrameNames)):
    framename = Str(FrameNames[i])
    arraynode = load_node(ArrayNodes[i])
    dictnode = load_node(DictNodes[i])
    framedata = SinglefileData(FrameData[i])
    DatafileWriter(framename, arraynode, dictnode, framedata)
    print(f'Adding {FrameNames[i]} to Datafile')

# Save the output data node
StoredFile = SinglefileData(tmp_path)
StoredFile.store()
StoredFile.label = f"{datafile_label.split('.')[0]}_{str(args.dirs)}"
print(f"""
Node Details:
PK: {StoredFile.pk}
Label: {StoredFile.label}
UUID: {StoredFile.uuid}""")