#!/usr/bin/env python3

# script that outputs all lammps lattice parameters used to identify triclinic cells for lammps.data files

# import modules
import sys
import numpy as np
from ase.io import read
import math

# load xyz frame using ase and wrap it,
frame = read(sys.argv[1])
frame.wrap(eps=1e-15)

# get the cell parameters from the xyz file
cell_params = frame.cell.cellpar()

# calculate all the quantities using all our known functions

class LammpsCell():
    """ Class to represent a LammpsCell object"""
    def __init__(self, cell_params):
        self.ase_cell_params = cell_params
        self.lx = cell_params[0]
        self.xy = cell_params[1] * math.cos(math.radians(cell_params[5]))
        self.xz = cell_params[2] * math.cos(math.radians(cell_params[4]))
        self.ly = np.sqrt(cell_params[1]**2 - self.xy**2)
        self.yz = ((cell_params[1] * cell_params[2] * math.cos(math.radians(cell_params[3]))) - (self.xy * self.xz)) /  (self.ly)
        self.lz = np.sqrt((cell_params[2]**2) - (self.xz**2) - (self.yz**2))
        self.lammps_parameters = {"lx": self.lx,
                                  "ly": self.ly,
                                  "lz": self.lz,
                                  "xy": self.xy,
                                  "xz": self.xz,
                                  "yz": self.yz}


cell = LammpsCell(cell_params)
print(cell.lammps_parameters)