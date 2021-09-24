#!/usr/bin/env python3

# import all the modules
import os, glob
from aiida import load_profile
from aiida.engine.processes.functions import workfunction
from aiida.orm import load_node
from aiida.engine import calcfunction
from aiida.orm.nodes.data.singlefile import SinglefileData
from aiida.plugins import DataFactory

# load profile
load_profile('samshepherd')

# load 'SinglefileData' and 'List' from the DataFactory
Singlefile = DataFactory('core.singlefile')

# Do the extra little situational little bit 
genPaths = os.path.join(os.getcwd(), 'kaolinite_*')
FramePaths = glob.glob(genPaths)
print(FramePaths)

@calcfunction
def DatafileWriter(Energy, Forces, Structure):
    """ This is the calcfunction that performs all writing functionality:
    Energy = The Dict storing the output_parameters of the CP2K calculation
    Forces = The ArrayData storing the atomic_forces of the CP2K calculation
    Structure = The StructureData node created by the CP2K calculation
    """

# Get all required nodes for the correct writing of the frame
    energyValue = Energy.attributes['energy']
    forceArray = Forces.get_array('forces')

# Implement the writer itself within these blocks
    Structure.export('tmp.xyz')
    tmpPath = os.path.join(os.getcwd(), 'tmp.xyz')
    lines = []
    with open(tmpPath, 'r') as handle:
        tmpData = handle.readlines()
    for jj, line in enumerate(tmpData):
        if 'Lattice' in line:
            words = line.split()[:9] + [' Properties=species:S:1:pos:R:3:forces:R:3', f'energy={energyValue}', 'pbc="T T T"']
            LatticeLine = " ".join(words)
            lines.append(LatticeLine)
        elif len(line.split()) == 4:
            words = line.split() + list(forceArray[jj-2,2:])
            AtomLine = '{0[0]:<2}{0[1]:>15}{0[2]:>15}{0[3]:>15}{0[4]:>13}{0[5]:>13}{0[6]:>13}'.format(words)
            lines.append(AtomLine)
        else:
            lines.append(line.split()[0])
    
    os.system('rm tmp.xyz')
    tmpFile = open('tmp.xyz', 'w+')
    for line in lines:
        tmpFile.writelines(f'{line}\n')
    
    tmpFile.close()
    StoredFile = SinglefileData(os.path.join(os.getcwd(), 'tmp.xyz'))
    StoredFile.label = 'kaolinite_NST'
    print(f"""
    Node Details:
    Label: {StoredFile.label}
    UUID: {StoredFile.uuid}""")
    os.system('rm tmp.xyz')
    return StoredFile

# write another calcfunction to pass all middle singlefiledatas to a single, large file
@calcfunction
def DatafileCollector(**kwargs):
    lines = []
    for singlefileData in kwargs.values():
        with singlefileData.open() as handle:
            data = handle.readlines()
        for line in data:
            lines.append(line)

    OverLordData = open('OverLord_kaolinite_NST.xyz', 'w+')
    for line in lines:
        OverLordData.writelines(f'{line}\n')
    OverLordData.close()

    StoredFile = SinglefileData(os.path.join(os.getcwd(), 'OverLord_kaolinite_NST.xyz'))
    StoredFile.label = 'kaolinite_NST_OverLordData'
    print(f"""
    Node Details:
    Label: {StoredFile.label}
    UUID: {StoredFile.uuid}""")
    return StoredFile

# wrap all in a workfunction
@workfunction
def TrackDataWriter():
    Singlefiles = {}
    for path in FramePaths:
        label = os.path.basename(path)
        CalcNode = load_node(label)
        Energy = CalcNode.outputs.output_parameters
        Forces = CalcNode.outputs.atomic_forces
        Structure = getattr(CalcNode.inputs.file, label)
        Singlefiles[os.path.basename(path)] = DatafileWriter(Energy, Forces, Structure)

    Stored = DatafileCollector(**Singlefiles)
    return Stored

# submit the function
TrackDataWriter()