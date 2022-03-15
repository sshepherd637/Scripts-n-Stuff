#!/usr/bin/env python3

########################################################
##           Script Created by Sam Shepherd           ##
##                     27/8/2021                      ##
########################################################

# Import the necessary modules to complete this script
import os
import numpy as np
from ase.io import read, write
from ase.units import Bohr
import argparse
import math 
import datetime

""" 
The first thing this script needs to do is analyse whether or not the simulation has exploded. If it has, it will try and grab all the frames prior to the extreme explosion
and use those as the useful frames for comparison later.

After this it will combine the forces and positions files together to generate a single 'xyz' file that can later be converted to the n2p2 format expected.
"""
# begin script timing 
begin_time = datetime.datetime.now()

# define all command line arguments
parser = argparse.ArgumentParser(description='Combine simulation outputs.')
parser.add_argument('-p', metavar='simulation prefix', type=str, help='simulation prefix used by i-pi to create the simulations')
parser.add_argument('-a', metavar='atoms', type=int, help='The number of atoms within the original simulation frame')
parser.add_argument('-v', metavar='velocity', type=str, required=False, default='False', help='Add velocities to the output xyz file')
args = parser.parse_args()

try:
    lmp_file = 'lmp.out'    
except:
    lmp_file = 'lmp_' + args.p.split('_')[1] + '.out'

eng_frames = args.p + '.out'
pdb_frames = args.p + '.pos_0.pdb'
for_frames = args.p + '.for_0.xyz'

if args.v == 'True':
    vel_frames = args.p + 'vel_0.xyz'

nAtoms = args.a 

# Read the frames in their totality from the pdb file, try except block to catch ValueErrors
try: 
    print(f"""Attempting to read {pdb_frames}...""")
    frames = read(pdb_frames, ':')
    print(f"""{pdb_frames} read successfully!...""")
except ValueError:
    print("""Simulation frames contain misrepresentations...
Working to correct...""")
    filepath = os.path.join(os.getcwd(), pdb_frames)
    with open(filepath, 'r') as handle:
        data = handle.readlines()
    frame_counter = -1
    for ii, line in enumerate(data):
        if 'TITLE' in line:
            frame_counter += 1
        if 'ATOM' in line and len(line.split()) != 11:
            frame = math.floor(ii/(nAtoms+3))
            print(f"""Frames unrecoverable beyond {frame}...
Saving all previous files for use...""")
            break
    frameEnd = frame * 275
    os.system(f"head -n {frameEnd} '{pdb_frames}' >> tmp.pdb")
    print("""Creating temporary frame file...""")
    frames = read('tmp.pdb', ':')
    print("""Deleting temporary frame file...""")
    os.system('rm tmp.pdb')
except:
    print("Unexpected Error")
    raise 

# With the positions now correct, and the number of frames we need, the file can work with the forces files.
filepath = os.path.join(os.getcwd(), for_frames)
print(f"""Attempting to read {for_frames}...""")
with open(filepath, 'r') as handle:
    forcefile = handle.readlines()
TotForceArray = np.zeros((nAtoms,3,len(frames)))
counter = 0
numLines = len(frames)*(nAtoms+2)
print("""Creating force array...""")
for ii in range(0, numLines, (nAtoms+2)):
    frameforceArray = np.zeros((nAtoms, 3))
    for jj in range((nAtoms+2)):
        if len(forcefile[ii+jj].split()) == 4:
            forces = [float(x) for x in forcefile[ii+jj].split()[1:]]
            frameforceArray[jj-2,:] = forces
    TotForceArray[:,:,counter] = frameforceArray
    counter += 1

if args.v == 'True':
    filepath = os.path.join(os.getcwd(), vel_frames)
    print(f"""Attempting to read {vel_frames}...""")
    with open(filepath, 'r') as handle:
        velfile = handle.readlines()
    TotVelArray = np.zeros((nAtoms,3,len(frames)))
    counter = 0
    numlines = len(frames)*(nAtoms+2)
    print("""Creating velocity array...""")
    for ii in range(0, numLines, (nAtoms+2)):
        framevelArray = np.zeros((nAtoms, 3))
        for jj in range((nAtoms+2)):
            if len(velfile[ii+jj].split()) == 4:
                velocities = [float(x) for x in velfile[ii+jj].split()[1:]]
                framevelArray[jj-2,:] = forces
        TotVelArray[:,:,counter] = framevelArray
        counter += 1

# with the positions and forces now accuately gathered, we need to use another file to get the energies out as predicted by the NNP
print("""Creating energy array...""")
EnergyArray = np.genfromtxt(eng_frames)

# with the forces and the positions now together, we are going to edit the frames from the pdb file to be more suitable for our needs, i.e. positions and forces
"""
UNITS NOTE:
POSITIONS/DISTANCES = ATOMIC UNITS I.E. BOHR
FORCES = ATOMIC UNITS
"""

pdbArrays = ['atomtypes', 'bfactor', 'occupancy', 'residuenames', 'residuenumbers']
print("""Creating output xyz file...""")
for ii, frame in enumerate(frames):
    for anArray in pdbArrays:
        try:
            del frame.arrays[anArray]
        except:
            None
    frame.new_array('forces', TotForceArray[:,:,ii], dtype=float)
    if args.v == 'True':
        frame.new_array('velocities', TotVelArray[:,:,ii], dtype=float)
    frame.set_cell(frame.cell / Bohr)
    frame.set_positions(frame.positions / Bohr)
    frame.info['energy'] = EnergyArray[ii,4]

print("""Writing output xyz file...""")
write("MDSimulation.xyz", frames)

# Finally, convert this data to n2p2 data and remove both the previous xyz file
#print("""Converting xyz output to n2p2 output...""")
#os.system('xyz2n2p2.py MDSimulation.xyz')
#os.system('rm MDSimulation.xyz')

# Finish script timing
end_time = datetime.datetime.now()
runtime = end_time - begin_time
print(f"""\n...Script executed in {runtime}""")
