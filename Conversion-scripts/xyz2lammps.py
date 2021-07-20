#!/usr/bin/env python3

# This script will convert xyz file data to lammps compatible format. This script will constantly update as required to deal with various different neural network atom assignment

# import modules
import sys
from ase.io import read
from ase.calculators.lammps import Prism, convert

# load the file to convert to lammps format as a sys argument
frame = read(sys.argv[1])

# define a swap dict to convert all element numbers to atomic assigned numbers
species_2_assigned = {
    1: 1,
    8: 2,
    13: 3,
    14: 4
}

# get all the useful information from the ase frame
positions = frame.arrays['positions']
chemical_species = frame.arrays['numbers']

# specify a new file to write the output too
new_file = open('data.lmp', 'w+')

# get important lammps parameters
xhi, yhi, zhi, xy, xz, yz = convert(Prism(frame.get_cell()).get_lammps_prism(), "distance",
                                        "ASE", 'metal')

# take care of some of the initial quick writing
format_line = [len(chemical_species), len(species_2_assigned), xhi, yhi, zhi, xy, xz, yz]
new_file.writelines('data.lmp (written by xyz2lammps.py)\n\n{0[0]:<7}atoms\n\n{0[1]:<7}atom types\n\n0.0{0[2]:>20}  xlo xhi\n0.0{0[3]:>20}  ylo yhi\n0.0{0[4]:>20}  zlo zhi\n{0[5]:<20}{0[6]:>20}{0[7]:>20} xy xz yz\n\n'.format(format_line))

# Get the chemical masses and write them. Handy using the chemical species
new_file.writelines('Atoms\n\n')

for i in range(len(positions)):
    positions_list = [i+1, species_2_assigned[chemical_species[i]], positions[i][0], positions[i][1], positions[i][2]]
    atom_line = '\t{0[0]:<2}{0[1]:>3}{0[2]:>20}{0[3]:>20}{0[4]:>20}\n'.format(positions_list)
    new_file.writelines(atom_line)

