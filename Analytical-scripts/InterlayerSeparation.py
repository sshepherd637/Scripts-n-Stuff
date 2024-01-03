#!/usr/bin/env python3

""" 
Script that calls a secondary bash script to get individual frames and cut down on reading, then computes interlayer distance
BashScript (Frame) -> GetInterlayerDistance -> Interlayer Distance -> Results File
"""

import os, sys, subprocess
from ase.io import read
from ase.units import Bohr

def GetFrameNumbers(path, nAtoms):
    
    """
    Computes total number of frames in a file
    Returns nFrames -> int
    """
    
    FullPath = os.path.join(os.getcwd(), path)
    cmdList = ['wc', '-l', FullPath]
    cmd = subprocess.Popen(cmdList, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out = cmd.communicate()[0]
    nLines = int(out.split()[0])
    nFrames = int(nLines / (nAtoms+3))
    return nFrames

def GetInterlayerDistance(frame):
    
    """
    Computes the Interlayer Distance of a given frame
    Returns formatted IntD -> string
    """

    Fnumber = os.path.basename(frame).split('_')[-1].split('.')[0]
    F = read(os.path.join(os.getcwd(), frame))
    F.set_cell(F.cell * Bohr)
    F.set_positions(F.positions * Bohr)
    MidPoint = F.cell.lengths()[2] / 2
    Opos, Hpos =[], []
    for atom in F:
        if atom.position[2] > (MidPoint-1) and atom.symbol == 'O':
            Opos.append(atom.position[2])
        elif atom.position[2] < MidPoint and atom.symbol == 'H':
            Hpos.append(atom.position[2])
    Opos.sort()
    Hpos.sort()
    O = Opos[0] # lowest = first one in the sorted list
    H = Hpos[-1] # highest = last one in the sorted list
    output = f'{Fnumber}{(O-H):15.5f}{O:15.5f}{H:15.5f}{MidPoint:15.5f}'
    return output



if __name__ == '__main__':
    nFrames = GetFrameNumbers(sys.argv[1], 272)

    if not os.path.exists(os.path.join(os.getcwd(), 'InterD.out')):
        os.mknod('InterD.out')

    with open('InterD.out', 'a+') as handle:
        handle.writelines(f'# Frame          InterD          Low Oxygen          High Hydrogen           Midpoint of Cell')

        for f in range(1, nFrames):
            cmdList = f'OFG.sh {f}'
            os.system(cmdList)
            fName = f'Frame_{f}.pdb'
            IntD = GetInterlayerDistance(fName)
            rmvCmd = f'rm {fName}'
            os.system(rmvCmd)
            with open('InterD.out', 'a+') as handle:
                handle.writelines(f'{IntD}\n')
        if f % 1000 == 0:
            print(f'Frames {nFrames}: {f}')
        
