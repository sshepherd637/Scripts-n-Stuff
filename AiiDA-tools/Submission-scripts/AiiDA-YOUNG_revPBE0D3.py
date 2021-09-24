# -*- coding: utf-8 -*- 
# pylint: disable=invalid-name

""" This script is used to run/test the water molecules aiida run using cp2k on young"""

""" In order for this script to operate, the following must be specified to the file and then to builder...
- The basis_set File --- Stored as a node, hence callable
- The potential File --- Stored as a node, hence callable
- The structure File --- Unique per calculation and created within the file
- The DFTD3 data File --- Stored as a node, hence callable
- The parameter Dictionary --- Unique per calculation and created within the file """

# Import the required modules to run this script
import os, sys
import glob
import ase.io
import numpy as np

# Import AiiDA
import aiida
from aiida.engine import submit
from aiida.orm import Code, Dict, SinglefileData, StructureData

# using glob to enter each individual directory and get the system_name
dir_paths = os.path.join(os.getcwd(), 'kaol_*') # Change this part to refer to different directories
pwd = os.getcwd()
dir_names = glob.glob(dir_paths)
for d in dir_names:
    os.chdir(d)
    config_files = os.path.join(os.getcwd(), '*.xyz') # This gets the structure file 
    config_file = glob.glob(config_files)[0]
    system_name = os.path.basename(config_file).split('.')[0]
    print(system_name)
    system_file = system_name +'.xyz'
    structure = StructureData(ase=ase.io.read(config_file)) # Creation of the AiiDA structure node

# Definition of the Basis-Sets file used within this calculation
    basis_set = load_node(label='GTH_BASIS_SET')

# Definition of the Potentials file used within this calculation
    potential_file = load_node(label='POTENTIAL')

# Definition of the DFTD3 parameter file used within this calculation
    DFTD3_file = load_node(label='DFTD3_DATA')

# Definition of the Parameter Dictionary
    params_dictionary = Dict(
	    dict = {
        'FORCE_EVAL': {
            'METHOD': 'Quickstep',
            'DFT': {
                'BASIS_SET_FILE_NAME': 'GTH_BASIS_SETS',
                'POTENTIAL_FILE_NAME': 'POTENTIAL',
                'MGRID': {
                        'CUTOFF': 400,
                },
                'XC': {
                    'XC_FUNCTIONAL': {
                        'PBE': {
                            'PARAMETRIZATION': 'REVPBE',
                        },
                    },
                    'VDW_POTENTIAL': {
                        'POTENTIAL_TYPE': 'PAIR_POTENTIAL',
                        'PAIR_POTENTIAL': {
                            'TYPE': 'DFTD3',
                            'R_CUTOFF': 15,
                            'LONG_RANGE_CORRECTION': 'TRUE',
                            'REFERENCE_FUNCTIONAL': 'revPBE',
                            'PARAMETER_FILE_NAME': 'dftd3.dat',
                        },
                    },
                    'XC_GRID': {
                        'XC_DERIV': 'SPLINE2',
                    },
                },
                'QS': {
                    'EPS_DEFAULT': 1.0e-12,
                    'EPS_PGF_ORB': 1.0e-14,
                    'EXTRAPOLATION': 'USE_GUESS',
                    'EXTRAPOLATION_ORDER': 5,
                },
                'SCF': {
                    'SCF_GUESS': 'RESTART',
                    'MAX_SCF': 50,
                    'EPS_SCF': 5.0e-7,
                    'OT': {
                        'MINIMIZER': 'DIIS',
                        'PRECONDITIONER': 'FULL_ALL',
                    },
                    'OUTER_SCF': {
                        'MAX_SCF': 20,
                        'EPS_SCF': 5.0e-7,
                    },
                },
            },
                'PRINT': {
		    'FORCES': {
		        '_' : 'ON',
		    },
	        },
	        'SUBSYS': {
                    'TOPOLOGY': {
                        'COORD_FILE_NAME': system_file,
                        'COORD_FILE_FORMAT': 'XYZ'  
                    },
                    'CELL': {
                        'A': '{:<15}  {:<15}  {:<15}'.format(*[structure.get_ase().cell[0][i] for i in range(3)]),
                        'B': '{:<15}  {:<15}  {:<15}'.format(*[structure.get_ase().cell[1][i] for i in range(3)]),
                        'C': '{:<15}  {:<15}  {:<15}'.format(*[structure.get_ase().cell[2][i] for i in range(3)]),
                    },
                    'KIND': [
                        {
                            '_': 'O',
                            'BASIS_SET': 'TZV2P-GTH',
                            'POTENTIAL': 'GTH-PBE-q6'
                        },
                        {
                            '_': 'H',
                            'BASIS_SET': 'TZV2P-GTH',
                            'POTENTIAL': 'GTH-PBE-q1'
                        },
                        {
                            '_': 'Al',
                            'BASIS_SET': 'DZVP-GTH',
                            'POTENTIAL': 'GTH-PBE-q3'
                        },
                        {
                            '_': 'Si',
                            'BASIS_SET': 'DZVP-GTH',
                            'POTENTIAL': 'GTH-PBE-q4'
                        }
                    ],
                },
            },
	    'GLOBAL': {
		    'RUN_TYPE': 'ENERGY_FORCE',
	    }, 
        })

# Use the aiida method to construct this method by loading the appropriate code etc..
    code = load_code('cp2k_code@Young')
    builder = code.get_builder()
    builder.parameters = params_dictionary
    builder.file = {
	    system_name: structure,
            'basis_sets' : basis_set,
	    'pseudopotentials' : potential_file,
	    'dftd3_data' : DFTD3_file
    }

# Use builder.metadata to specify the additional settings of the calculation 
### THIS PART IS EXTREMELY SYSTEM SPECIFIC ###
    builder.metadata.computer = load_computer('Young')
    builder.metadata.options.account = 'Gold'
    builder.metadata.options.resources = {'parallel_env': 'mpi', 'tot_num_mpiprocs': 80}
    builder.metadata.options.parser_name = 'cp2k_advanced_parser'
    builder.metadata.options.max_wallclock_seconds = 1 * 20 * 60
    builder.metadata.label = system_name
    builder.metadata.description = f'Runner for {system_name} configuration files on Young'


# Submit the calculation
    submit(builder)
    os.chdir(pwd)

