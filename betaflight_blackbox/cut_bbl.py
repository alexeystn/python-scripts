import re
import os

input_filename = 'R_20220120.bbl'

header = b'H Product:Blackbox'
output_path = './output/'

with open(input_filename, 'rb') as f:
    data = f.read()

pos = []  # header positions
for m in re.finditer(header, data):
    pos.append(m.start())

print(pos)

if not os.path.exists(output_path):
    os.mkdir(output_path)

for i in range(len(pos)-1):
    if pos[i+1]-pos[i] > 5000:  # do not save too short files
        output_filename = output_path + input_filename[:-4] + \
                       '_{0:02d}.bbl'.format(i+1)
        with open(output_filename, 'wb') as f:
            f.write(data[pos[i]:pos[i+1]])
