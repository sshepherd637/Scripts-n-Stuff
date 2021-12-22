#!/usr/bin/env python3

# Simple quick script to update the headers on ipi.xyz files to the correct frame values

# Import modules
import os, sys 
import numpy as np

from ase.io import read, write
from ase.units import Bohr 

# if sys.argv[2] exists, then the units need to be converted
# Load the xyz frame with the normal header

def main():
    frame = read(sys.argv[1])

    if sys.argv[2]:
        frame.set_cell(frame.cell / Bohr)
        frame.set_positions(frame.positions / Bohr)
        write('Units.xyz', frame)
        #os.system(f'mv Units.xyz {sys.argv[1]}')

# change the line here
    with open(os.path.join(os.getcwd(), sys.argv[1]), 'r') as handle:
        data = handle.readlines()

    cellParams = frame.get_cell_lengths_and_angles()
    cellParamsStrs = [str(x) for x in cellParams.tolist()]
    cellPart = '   '.join(cellParamsStrs)
    SmallAdd = str('{atomic_unit}')
    newLine = f"# CELL(abcABC):   {cellPart} cell{SmallAdd}  Traj: positions{SmallAdd} Step:          0  Bead:       0\n"
    data[1] = newLine

# write new file now
    with open('tmp.xyz', 'w+') as output:
        for line in data:
            output.writelines(f'{line}')

if __name__ == "__main__":
    main()

