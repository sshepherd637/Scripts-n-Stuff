#!/usr/bin/env python3

# This script will transform the output .xyz files to a readable n2p2 file using a command line argument of the desired dataset to be transformed
# By Sam Shepherd
# Dated 23/6/2021

# Using ASE, we can make this process pretty painless       
from ase.io import read, write
import sys
import numpy as np

# Load the dataset as the first system argument
frames = read(sys.argv[1], ':')

# Some formatting to be used before the loop
newfile = open('input.data', 'w+')

# define some useful helper functions to correctly format the atom lines
def lattice_writer(frame):
    params = frame.cell
    lparams = [params[0], params[1], params[2]]
    aparams = np.array(lparams)
    for i in range(aparams.shape[0]):
        newfile.writelines(f'lattice {aparams[i][0]} {aparams[i][1]} {aparams[i][2]}\n')

def atom_writer(frame):
    species = frame.arrays['numbers']
    positions = frame.arrays['positions']
    try:
        force = frame.arrays['force']
    except:
        force = frame.arrays['forces']
    for i in range(species.shape[0]):
        newfile.writelines(f'atom {positions[i][0]} {positions[i][1]} {positions[i][2]} {species_dict[species[i]]} 0.0 0.0 {force[i][0]} {force[i][1]} {force[i][2]}\n') # 0.0 = charge as not implemented

species_dict = { # add to as required
    1 : 'H',
    8 : 'O',
}
# Work with each frame in a for loop, iterate and print as required
for i in range(len(frames)):
    newfile.writelines(f'begin\ncomment -> Created by the xyz2n2p2 python script\n')
    lattice_writer(frames[i])
    atom_writer(frames[i])
    newfile.writelines(f'energy {frames[i].get_total_energy()}\ncharge 0.0\nend\n')
