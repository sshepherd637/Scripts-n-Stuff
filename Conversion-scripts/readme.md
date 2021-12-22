# Arguments

All these scripts are hopefully self explanatory, just make sure the format of the xyz file matches that expected for these codes.

To run these conversion scripts, pass the file to convert as a command line argument to the script

#### MDCombine.py

This file is used to combine the results of i-pi driven molecular dynamics using the lammps engine coupled with the **fix-nnp** command and takes two command line arguments, the simulation file prefix, (denoted `SomePrefix`) as `-p` and the number of atoms in each frame as `-a`.

As such, this file must be run in a directory where the output of these simulations exists, in particular it needs access to...
1. `SomePrefix.for_0.xyz` : the file containing all the forces (xyz based).
2. `SomePrefix.pos_0.pdb` : the file containing all the cell parameters and positions (pdb based).
3. `lmp_SomePrefix.out` : the file containing all the system energies and other output from lammps (lammps output).
Where ***SomePrefix*** typically contains the prefix defined in i-pi's `input.xml` file, and typically contains the simulation number if a large amount of simulations are being performed.
If this is not the case, either edit this part of the script to better suit, or eventually I might get around to adding a command line argument to specify this.

For the sake of simplicity, this script calls on `xyz2n2p2.py`, another script found within this directory, make sure the path is available to this script and that the command.
    
    xyz2n2p2.py SomeSimulationFile.xyz

Runs properly.

#### xyz2n2p2.py

This script does exactly what the name suggests it does, and converts xyz data to n2p2 readable formats.

#### xyz2lammps.py

This script converts xyz data to a lammps digestible format, as required by the n2p2 pair style within lammps. 

#### xyz2ipi.py 

This script just changes the lattice line within the xyz file to better suit the ipi wrapper.
