#!/usr/bin/env python3

# Very particular script to create xyz files from cp2k supercells created by phonopy.

import sys

### FUNCTION DEFINITION ###
def read_cp2k(file):
    """
    Function that reads a cp2k input file and parses all the necessary cell information from that file.
    """
    with open(file, 'r') as handle:
        data = handle.readlines()
    
    cell = False
    structure = False
    cell_d, structure_d = [], []
    for line in data:
        if cell == True and len(line.split()) == 4:
            cell_data = [float(x) for x in line.split()[1:]]
            cell_d.append(cell_data)
        if structure == True and len(line.split()) == 4:
            atom_data = line.split()
            atom_string = f'{atom_data[0]}    {float(atom_data[1]):>15.10f}{float(atom_data[2]):>15.10f}{float(atom_data[3]):>15.10f}'
            structure_d.append(atom_string)

            
        if "&COORD" in line:
            structure = True
        elif "&CELL" in line:
            cell = True
        elif "&END COORD" in line:
            structure = True
        elif "&END CELL" in line:
            cell = False

    return cell_d, structure_d 

def write_xyz(cell_d, structure_d):
    """
    Function that writes an xyz file output.
    """
    with open('output.xyz', 'w+') as handle:
        handle.writelines(f'{len(structure_d)}\n')
        handle.writelines(f'Lattice="{cell_d[0][0]} {cell_d[0][1]} {cell_d[0][2]} {cell_d[1][0]} {cell_d[1][1]} {cell_d[1][2]} {cell_d[2][0]} {cell_d[2][1]} {cell_d[2][2]}" Properties=species:S:1:pos:R:3 pbc="T T T"\n')
        for atom in structure_d:
            handle.writelines(f'{atom}\n')

    return 

if __name__ == "__main__":
    cd, sd = read_cp2k(sys.argv[1])
    write_xyz(cd, sd)
