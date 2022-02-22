#!/usr/bin/env python3
# script to combine the calculated forces of a job and combine them with the original position file to rewrite the new position file to be used with the machine learning models.

import time
import argparse
import os, sys
import glob
import aiida
from aiida.orm import load_node
from ase.io import read, write
from ase.units import Bohr
import numpy as np

# definition of the listtostring function that is used often enough to warrant this.
def listtostring(list):
    str1 = ' '
    return str1.join(list)

### COMMAND LINE PARSER ###
parser = argparse.ArgumentParser(description='Writes node files within each directory')
parser.add_argument('-l', '--label', help='General label format prior to wildcard characters', required=False, type=str)
parser.add_argument('-u', '--units', help='Output units', required=True, type=str.lower, choices=['au', 'ev'], default='au')
parser.add_argument('-w', '--where', help="Location of the output datafile", type=str, choices=['big', 'small'], required=True, default='big')
parser.add_argument('-p', '--path', help='Path to the xyz files', required=False, type=str, default=os.getcwd())
parser.add_argument('-e', '--extension', help='Extensions to the node label beyond the directory name', required=False, type=str)
parser.add_argument('-f', '--force_name', help='Name of the Force array within the Array node', type=str, required=False, default='forces')
args = parser.parse_args()
print(args)
### END PARSER ###

# Define some argument choices up here for ease of use later
if args.units == 'ev':
    UNITFACTOR = 1
elif args.units == 'au':
    UNITFACTOR = Bohr

# We need to create an appropriate loop to go into each directory
path_string = os.path.join(args.path, f'{args.label}*')
dir_names = glob.glob(path_string)
parent_dir = os.getcwd()

# loading the aiidav profile
aiida.load_profile('samshepherd')

### We can set up the for loop to load the .xyz file, the array and the parameters ###

# This block takes us into each directory for the calculation label
for ii in dir_names:
    os.chdir(ii)
    if args.label is not None:
        label = args.label + f'_{os.path.basename(ii).split("_")[-1]}' + '_' + args.extension
        xyzPath = ii + f'/{os.path.basename(ii).split("/")[-1]}' + '.xyz'
    elif args.label is None:
        print(os.path.basename(ii))
        label = os.path.basename(ii).split("/")[-1] + '_' + args.extension

    node = load_node(label)
    ArrayNode = node.outputs.atomic_forces
    ForceArray = ArrayNode.get_array(args.force_name)

# This block gets the required outputs from the calculation node and gets the xyzData for the xyzFile
    ParamDict = node.outputs.output_parameters
    energy = ParamDict['energy']
    if args.units == 'ev':
        energy = float(energy) * 27.211396641308

    if args.label:
        xyzHandle = xyzPath 
    else:
        xyzHandle = label + '.xyz'
    xyzFile = os.path.join(os.getcwd(), xyzHandle)
    with open(xyzFile, 'r') as xyzSwinger:
        xyzData = xyzSwinger.readlines()
    
# This block handles the file location and name
    fileString = f'results_{args.units}.xyz'
    if args.where == 'big':
        os.chdir(parent_dir)
        datafile = open(fileString, 'a+')
    elif args.where  == 'small':
        datafile = open(fileString, 'w+')

### We now have the required files and arrays opened, so we can now write/append a new xyzFile ###

# Handy to load up the force array prior to 
    NpForceArray = np.array(ForceArray)  
    if args.units == 'ev':
        NpForceArray = NpForceArray * 51.422067
        
    for jj, line in enumerate(xyzData):
        if jj == 0:
            natoms = line.split()[0]
            datafile.writelines(f'{natoms}\n')
        if jj == 1:
            lattice_line = line.split()
            if lattice_line[-1] == 'T"':
                shorter_line = lattice_line[:-4]
                for kk in range(len(shorter_line)):
                    shorter_line[kk] = shorter_line[kk].replace('"', '')
                shorter_line[0] = f'Lattice="{str(float(shorter_line[0].split("=")[-1]) / UNITFACTOR)}'
                shorter_line[1:9] = [str((float(x) / UNITFACTOR)) for x in shorter_line[1:9]]  
                shorter_line[8] = f'{shorter_line[8]}"'
                eV_str = 'energy=' + str(energy)
                shorter_line.append(eV_str)
                datafile.writelines(f'{listtostring(shorter_line)} pbc="T T T"\n') 
            else:
                del lattice_line[-1]
                for ll in range(len(lattice_line)):
                    lattice_line[ll] = shorter_line[ll].replace('"', '')
                lattice_line[1] = str(float(lattice_line[0].split('=')[-1]) / UNITFACTOR)
                lattice_line[1:10] = [str((float(x) / UNITFACTOR)) for x in lattice_line[1:9]]
                lattice_line[1] = f'Lattice="{lattice_line[1]}'
                lattice_line[9] = f'{lattice_line[9]}"'
                lattice_line[-1] = lattice_line[-1] + str(energy)
                lattice_str = listtostring(lattice_line)
                datafile.writelines(f'{lattice_str} pbc="T T T"\n')
        if jj >= 2 and jj <= (int(natoms) + 1):
            if NpForceArray.shape[0] > int(natoms):
                placeholder = jj - 1
            elif NpForceArray.shape[0] == int(natoms):
                placeholder = jj - 2
            atom_line = line.split()
            del atom_line[4:]
            atom_line[1:4] = [str(round((float(mm) / UNITFACTOR), 10)) for mm in atom_line[1:4]]
            atom_line.append('%.9f'%(float(NpForceArray[:,2][placeholder])))
            atom_line.append('%.9f'%(float(NpForceArray[:,3][placeholder])))
            atom_line.append('%.9f'%(float(NpForceArray[:,4][placeholder])))

            AtomStr = '{0[0]:<2}{0[1]:>18}{0[2]:>18}{0[3]:>18}{0[4]:>20}{0[5]:>20}{0[6]:>20}'.format(atom_line)
            datafile.writelines(f'{AtomStr}\n')


    # little output to know that one is written
    print(f'adding the recalculated forces and energy of {label} to the new datafile')
    
    # addition of the if/elif statement for the file output and location
    if args.where == 's':
        os.chdir(parent_dir)
