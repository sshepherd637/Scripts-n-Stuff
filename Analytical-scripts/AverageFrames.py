#!/lustre/shared/ucl/apps/python/bundles/python38-5.0.0/venv/bin/python3
import os, re 
import numpy as np
from ase.io import read, write
import sys

frame_file = sys.argv[1]

# read the frames in
frames = read(frame_file, ':')

# create energy array
energies = np.zeros(len(frames))

# fill energy array
for i in range(len(frames)):
	energy = frames[i].get_potential_energy()
	energies[i] = energy

# calculate the mean and average arrays
mean = np.mean(energies)
print(mean)

meaned_energies = energies - mean

# loop through all frames and replace energy in file
counter = 0
new_file = open('Kaolinite.xyz', 'w+')

file_path = os.path.join(os.getcwd(), frame_file)
with open(file_path, 'r') as handle:
	data = handle.readlines()

for i in range(len(data)):     
	if 'Lattice' in data[i]:             
		words = data[i].split(' ')             
		for word in words:                     
			if re.search('energy.+', word):                             
				eng_ind = word             
		eng_str = eng_ind.split('=')[0] + '=' + str(meaned_energies[counter])             
		index = words.index(eng_ind)
		del(words[index])
		lattice_line = f"{words[0]} {words[1]} {words[2]} {words[3]} {words[4]} {words[5]} {words[6]} {words[7]} {words[8]} {words[9]} {words[10]} {words[11]} {words[12]} {eng_str}\n" 
		new_file.writelines(lattice_line)
		counter += 1
	else:
		new_file.writelines(f'{data[i]}')
