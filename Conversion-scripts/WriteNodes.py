#!/usr/bin/env python3

###########################
# Created by Sam Shepherd #
#   Checks all nodes and  #
#   attempts to write a   #
# datafile containing all #
#        the files        #
#       13/12/2021        #
###########################

# Import modules.
import os, sys 
import glob
import re
from ase.io.bundletrajectory import main
import numpy as np 
import argparse

from aiida import load_profile
from aiida.common.exceptions import NotExistent
from aiida.orm import load_node
from ase.io import read, write
from ase.units import Bohr

# Load AiiDA profile
load_profile('samshepherd')

# Define the command line parser and deal with choices appropriate to the start of the script
parser = argparse.ArgumentParser(description='Provenance tracking combination script for all datafiles')
parser.add_argument('dirs', metavar='Directories', type=str, help='general directory name')
parser.add_argument('--units', metavar='Output units', help='Output units', required=True, type=str.lower, choices=['au', 'ev'], default='au')
parser.add_argument('--add', metavar='Additional label text', type=str, required=False, help='additional text to help identify labels')
parser.add_argument('--forces', metavar='Force array name', help='Name of the Force array within the Array node', type=str, required=False, default='forces')
parser.add_argument('--output', metavar='Output location', type=str, required=False, help='location to write the output file to', default=os.getcwd())
parser.add_argument('--keep_outputs', metavar='Keep intermediate `result.xyz` files', type=bool, required=False, help='Determines whether intermediate files are kept', default=False)
args = parser.parse_args()

def mainFunc(args):
    genDirs = f'{args.dirs}*' 
    if args.units == 'au':
        EngVar, ForcVar = 1, 1
        posVar = Bohr  
    else:
        EngVar, ForcVar = 27.211396641308, 51.422067
        posVar = 1

# Assess all directories within this directory with form of `dirs` in arguments
    allDirs = glob.glob(genDirs)
    ParentWD = os.getcwd()

    newFrames = [] 
    for dir in allDirs:
        nodeLabel = f'{dir}{args.add}'
        try:
            node = load_node(nodeLabel)
        except NotExistent:
            print(f'{nodeLabel} not found... consider adding to fail nodes directory')
            raise
        os.chdir(dir)
        ogFrame = read(f'{dir}.xyz')
        # Load all other required values for the transformation of the original frame
        try: 
            engVal = node.outputs.output_parameters['energy']
            forNode = node.outputs.atomic_forces
        except NotExistent:
            print(f'Calculation {nodeLabel} did not return an output... consider adding it to fail nodes directory')
        forArray = forNode.get_array(args.forces)
        # If the length of the array is larger than the number of atoms, remove the top row
        if len(ogFrame.get_atomic_numbers()) < forArray.shape[0]:
            forArray = forArray[1:,:]
        if forArray.shape[1] > 3:
            forArray = forArray[:,2:]
        # Edit frame as required prior to addition of other information
        ogFrame.set_cell(ogFrame.cell / posVar)
        ogFrame.set_positions(ogFrame.positions / posVar)
        # Edit frame to include new information
        ogFrame.arrays['force'] = forArray.astype('float64') * ForcVar
        write('result.xyz', ogFrame)
    
        # Use a context manager to change the energy.
        resultPath = os.path.join(os.getcwd(), 'result.xyz')
        with open(resultPath, 'r') as handle:
            data = handle.readlines()
        
        with open('tmp', 'w+') as output:
            for line in data:
                if 'energy=' in line:
                    words = line.split()
                    for ii, word in enumerate(words):
                        if re.search('energy=', word):
                            engToChange = word
                            engIndex = words.index(word)
                            words[engIndex] = f"{engToChange.split('-')[0]}{str(engVal * EngVar)}"
                    EngString = ' '.join(words)
                    output.writelines(f'{EngString}\n')
                else:
                    output.writelines(f'{line}')
    
        # Do some editting of the code within this block to get the correct frame loaded and delete the old frame.
        os.system('mv tmp result.xyz')
        newFrame = read('result.xyz')
        os.system('rm result.xyz')
        write('result.xyz', newFrame)
        newFrames.append(newFrame)


        # Determine whether to delete intermediate files
        if args.keep_outputs != True:
            os.system('rm result.xyz')
        os.chdir(ParentWD)

    write(f'Kaolinite_revPBE0D3_{os.path.basename(args.output)}.{args.units}.xyz', newFrames)
    print(f'Kaolinite_revPBE0D3_{os.path.basename(args.output)}.{args.units}.xyz has been written.')

if __name__ == "__main__":
    mainFunc(args)


