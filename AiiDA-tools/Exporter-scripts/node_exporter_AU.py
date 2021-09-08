#!/usr/bin/env python3
# script to combine the calculated forces of a job and combine them with the original position file to rewrite the new position file to be used with the machine learning models.

import time
import os, sys
import glob
import aiida
from aiida.orm import load_node
from ase.io import read, write
from ase.units import Bohr
import numpy as np

def listtostring(list):
    str1 = ' '
    return str1.join(list)

# We need to create an appropriate loop to go into each directory
dir_prefix = sys.argv[1]
path_string = dir_prefix + '_*'
dir_paths = os.path.join(os.getcwd(), path_string)
dir_names = glob.glob(dir_paths)
parent_dir = os.getcwd()

# loading the aiidav profile
aiida.load_profile('samshepherd')

# now we can set up the for loop to load the .xyz file, the array and the parameters
for i in dir_names:
    label = os.path.basename(i)
    node = load_node(label)
    os.chdir(i)
    array = node.outputs.atomic_forces
    f_array = array.get_array('forces')
    
    param_dict = node.outputs.output_parameters
    energy = param_dict['energy'] 
    xyz_handle = label + '.xyz'
    xyz_file = os.path.join(os.getcwd(), xyz_handle)
    with open(xyz_file, 'r') as xyz_swinger:
        xyz_data = xyz_swinger.readlines()
    
    os.chdir(parent_dir)
    datafile = open('DATAFILE_AU.xyz', 'a+')

# we now have the required files and arrays opened, so we can now rewrite the .xyz file
    # best to separate out the array sections until I rewrite the parser
    f_array = np.array(f_array)
    x_force, y_force, z_force = f_array[:,2], f_array[:,3], f_array[:,4]    
    for i, line in enumerate(xyz_data):
        if i == 0:
            natoms = line.split()[0]
            datafile.writelines(f'{natoms}\n')
        if i == 1:
            lattice_line = line.split()
            if lattice_line[-1] == 'T"':
                shorter_line = lattice_line[:-4]
                for jj in range(len(shorter_line)):
                    shorter_line[jj] = shorter_line[jj].replace('"', '')
                shorter_line[0] = str(float(shorter_line[0].split('=')[-1]) / Bohr)
                shorter_line[1:9] = [str((float(x) / Bohr)) for x in shorter_line[1:9]]  
                shorter_line[0] = f'Lattice="{shorter_line[1]}'
                shorter_line[8] = f'{shorter_line[8]}"'
                eV_str = 'energy=' + str(energy)
                shorter_line.append(eV_str)
                datafile.writelines(f'pbc="T T T" {listtostring(shorter_line)}\n') 
            else:
                del lattice_line[-1]
                for jj in range(len(lattice_line)):
                    lattice_line[jj] = shorter_line[jj].replace('"', '')
                lattice_line[1] = str(float(lattice_line[0].split('=')[-1]) / Bohr)
                lattice_line[1:10] = [str((float(x) / Bohr)) for x in lattice_line[1:9]]
                lattice_line[1] = f'Lattice="{lattice_line[1]}'
                lattice_line[9] = f'{lattice_line[9]}"'
                lattice_line[-1] = lattice_line[-1] + str(energy)
                lattice_str = listtostring(lattice_line)
                datafile.writelines(f'pbc="T T T" {lattice_str}\n')
        if i >= 2 and i <= (int(natoms) + 1):
            if f_array.shape[0] > int(natoms):
                placeholder = i - 1
            elif f_array.shape[0] == int(natoms):
                placeholder = i - 2
            atom_line = line.split()
            del atom_line[4:]
            atom_line[1:4] = [str(round((float(jj) / Bohr), 10)) for jj in atom_line[1:4]]
            atom_line.append('%.9f'%(float(x_force[placeholder])))
            atom_line.append('%.9f'%(float(y_force[placeholder])))
            atom_line.append('%.9f'%(float(z_force[placeholder])))

            atom_str = '{0[0]:<2}{0[1]:>18}{0[2]:>18}{0[3]:>18}{0[4]:>20}{0[5]:>20}{0[6]:>20}'.format(atom_line)
            datafile.writelines(f'{atom_str}\n')


    # writing the new datafile 
    print(f'adding the recalculated forces and energy of {label} to the new datafile')

## TO-DO reoptimize this script after some corrections are made to various conversions ##
