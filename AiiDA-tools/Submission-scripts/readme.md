# Directory Details 
Submission scripts for various different CP2K calculations on various different computers

### Standard single-point calculations
The following scripts are for standard energy-force single point calculations:
1. `AiiDA-KELVIN_revPBED3.py`
2. `AiiDA-KELVIN_revPBE0D3.py`
3. `AiiDA-YOUNG_revPBED3.py`
4. `AiiDA-YOUNG_revPBE0D3.py`

The following scripts do a number of different things, depending on the suffix of the filename:
1. `AiiDA-KELVIN_revPBED3-wfn-pol.py`
2. `AiiDA-YOUNG_revPBED3-wfn-pol.py`

### List of suffixes:
-`initwfn`: Returns the calculated wavefunction to store it for future calculations. 
-`wfn`    : Uses a previously calculated wavefunction to attempt to cheapen the calculation.
-`pol`    : Calculates the polarization of the system.

