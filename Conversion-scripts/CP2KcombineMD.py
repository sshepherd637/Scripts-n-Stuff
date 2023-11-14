#!/usr/bin/env python3

########################################################
##           Script Created by Sam Shepherd           ##
##                      4/5/2023                      ##
########################################################

# Import modules to complete this script 
import numpy as np 
import argparse as ap
from ase.io import read, write

# Create parser for arguments
parser = ap.ArgumentParser(description='Combine the outputs of a CP2K MD simulation')
parser.add_argument('-pos', type=str, help='Position file')
parser.add_argument('-cell', type=str, help='Cell information')
parser.add_argument('-forc', type=str, help='Force file')
parser.add_argument('-natoms', type=int, help='Number of Atoms')
parser.add_argument('-out', type=str, help='Output filename')
args = parser.parse_args()

# Create function to parse energy 
def getForces(forc, length, natoms):
    forces = []
    with open(forc, 'r') as handle:
        data = handle.readlines()
    for line in data:
        if len(line.split()) == 4:
            AtomForces = [float(x) for x in line.split()[1:]]
            forces.append(AtomForces)
    ForceArray = np.array(forces)
    ForceArray = ForceArray.reshape(natoms, 3, length)
    return ForceArray

# Create function to incorperate forces and positions together
# Perform main loop

if __name__ == "__main__":
    frames = read(args.pos, ':')
    forces = getForces(args.forc, len(frames), args.natoms)
    cell = [float(x) for x in args.cell.split()]
    npcell = np.array(cell)
    npcell = npcell.reshape(3,3)
    for ii, frame in enumerate(frames):
        frame.set_cell(npcell)
        frame.new_array('forces', a=forces[:,:,ii])
        frame.pbc = [True, True, True]
        energy = frame.info['E']
        del frame.info['i']
        del frame.info['time']
        del frame.info['E']
        frame.info['energy'] = energy

    write(args.out, frames)
