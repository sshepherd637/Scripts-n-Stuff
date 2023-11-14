from ast import Add
from ase.io import read, write
from ase import build, Atoms
import numpy as np 
import argparse, sys, warnings, random, copy 

if not sys.warnoptions:
    warnings.simplefilter("ignore")

def MIC(vec,cell,icell):
  """
  Apply minimum image convention to a vector to account for
  periodic boundary conditions
  """

  ivc = np.dot(icell,vec)
  rvc = np.round(ivc)
  cvc = np.dot(cell,rvc)
  ovc = vec - cvc
  return ovc

# INPUT ARGUMENTS #
parser = argparse.ArgumentParser(description="Converter for BARE clay minerals to ClayFF readible structures for LAMMPS")
parser.add_argument("-i", "--input", required=True, help="Input file")
parser.add_argument("-o", "--output", required=False, default="clayff.data", help="Output file")
args = parser.parse_args()

xyz = read(args.input)
x_copy = copy.deepcopy(xyz)
cell = xyz.get_cell().T 
icell = np.linalg.inv(cell) 

def generate():
    ang2bohr = 1.8897261

    # get list of hydroxyl oxygens -> in a dry mineral these are the only groups of atoms described by bonding parameters using the ClayFF model
    all_oh = []
    just_oh = []
    for ii in range(len(xyz)):
        if (xyz[ii].symbol=='O'):
            oh = False
            for jj in range(len(xyz)):
                if (xyz[jj].symbol=='H'):
                    dr = np.linalg.norm(MIC(xyz[ii].position-xyz[jj].position,cell,icell))
                    if (dr<1.2):
                        oh = True
                        hval = jj
            if (oh==True):
                all_oh.append([ii,hval])  
                just_oh.append(ii)

    n_kaol = 272

    # ClayFF is mostly an ionic force field, so charges are VERY IMPORTANT, the other empty lists are placeholders for use later
    charge_dict = {1:0.425, 2:-0.95, 3:-1.05, 4:1.575, 5:2.1, 8:1.36, 10:1.575, 11:-1.1808, 12:-1.1688, 13:-1.2996, 14:-1.0808}
    types = [] 
    charges = [] 

    # Assignment loop for atomic types
    for ii, atom in enumerate(xyz):
        atom_type = 0
        if atom.symbol == 'H':
            atom_type = 1 # Hydrogen 
        elif atom.symbol == 'Si':
            atom_type = 5 # Silicon
        elif atom.symbol == 'Al':
            atom_type = 4 # Aluminium 
        elif atom.symbol == 'O':
            if ii in just_oh: # hydroxyl oxygen atom
                atom_type = 2
            else:
                atom_type = 3
        if atom_type == 0:
            print("Whoops, some unassigned atoms are left!")
            sys.exit(0)
        types.append(atom_type)

    for ii, atom in enumerate(xyz):
        charges.append(charge_dict[types[ii]])

    total_charge = sum(charges) # for kaolinite, a neutral system, this should equate to 0!
    if total_charge != 0: 
        print("Whoops, your neutral kaolinite system isn't neutral!")
        sys.exit(0)

    with open(args.output, 'w+') as handle:
        # Start of the LAMMPS file and definition of atoms, bonds and angles including numbers of each.
        handle.writelines(f"LAMMPS Description\n\n        {str(n_kaol)} atoms\n        {str(len(just_oh))} bonds\n        0 angles\n\n")
        handle.writelines(f"          14 atom types\n          2 bond types\n          2 angle types\n\n")
        # Definition of the simulation cell.
        handle.writelines(f"          0 {xyz.get_cell()[0,0]} xlo xhi\n          0 {xyz.get_cell()[1,1]} ylo yhi\n          0 {xyz.get_cell()[2,2]} zlo zhi\n          {xyz.get_cell()[0,1]} {xyz.get_cell()[0,2]} {xyz.get_cell()[1,2]} xy xz yz\n\n")
        # Definition of the atomic masses for each atom type.
        handle.writelines(f"Masses\n\n  1 1.008   # Hydrogen\n  2 15.999  # Hydroxyl oxygen\n  3 15.999  # Bridging oxygen\n  4 26.982  # Octahedral aluminium\n  5 28.085  # Tetrahedral silicon\n")
        handle.writelines(f"  6 15.9994 # Water oxygen\n  7  1.0080 # Water hydrogen\n  8 24.3050 # Magnesium defect\n  9 22.9900 # Aqueous sodium ion\n 10 26.982  # Tetrahedral aluminium\n")
        handle.writelines(f" 11 15.999  # Bridging oxygen with octahedral substitution\n 12 15.999  # Bridging oxygen with tetrahedral substitution\n 13 15.999  # Bridging oxygen with double substitution\n 14 15.999  # Hydroxyl oxygen with substitution\n\n")
        # Definition of Bond and Angle function parameters for the different types. 
        handle.writelines(f"Bond Coeffs\n\n  1    1.7857912 0.2922036228 -0.344065918968 0.23632849592496\n2    1.78    0.2708585 -0.327738785 0.231328959\n\n")
        handle.writelines(f"Angle Coeffs\n\n  1    0.0239 110\n  2    0.0700  107.400000\n\n")
        # Definition of Atom types, symbols and positions
        handle.writelines(f"Atoms\n\n")
        for ii, atom in enumerate(xyz):
            handle.writelines(f"{ii+1} 1 {types[ii]} {charges[ii]} {atom.position[0]} {atom.position[1]} {atom.position[2]}\n")
        # Definition of defined bonds and angles
        handle.writelines(f"Bonds\n\n")
        for ii in range(len(all_oh)):
            handle.writelines(f"{ii+1} 1 {all_oh[ii][1]+1} {all_oh[ii][0]+1}\n")
    
    return 

if __name__ == "__main__":
    generate()
