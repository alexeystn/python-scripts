import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter

n = 1

filenames = ['rdr', 'dsg']
titles = ['Пилоты гонки RDR ВКТ',
          'Пилоты гонок Drone Sports']

dist = np.genfromtxt('age_{0}.txt'.format(filenames[n]))
bins = np.arange(0,60,5)
fig = plt.figure(figsize=(6,3), dpi=100)
plt.hist(dist, bins=bins, width=4,
         weights=np.ones(len(dist))/len(dist))
plt.title(titles[n])
plt.xlabel('Возраст')
plt.ylabel('Кол-во пилотов')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
fig.subplots_adjust(bottom=0.15, top=0.85, left=0.15)
plt.grid(True)
plt.savefig(filenames[n] + '_age.png')
plt.show()
