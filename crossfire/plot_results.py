import numpy as np
from matplotlib import pyplot as plt
import json


#def plot_histogram(values, limits):
import re

def remove_outliers(values):
    values = np.array(values)
    m = np.mean(values)
    s = np.std(values)
    mask = np.abs(values - m) < 2*s
    d = values[mask]
    print('{0:.1f}%'.format(100*len(d)/len(values)))
    return d
    

a_file = open("data_tx2rx.json", "r")
result = json.load(a_file)
a_file.close()

legend = []

for k in result:
    latency = result[k][:500]
    latency = remove_outliers(latency)

    mu = np.mean(latency)
    sigma = np.std(latency)

    if k.startswith('elrs'):
        k = k.upper()
    else:
        k = k.capitalize()
        
    text = r'$\mu$ = {0:.1f} ms'.format(mu)
    name = re.findall(r'[A-z]+', k)[0] + ' ' + \
           re.findall(r'\d+', k)[0] + ' Hz: '
    legend.append(name + text)

    #bins=np.arange(0.5, 40.5, 1)
    bins=np.arange(0, 40, 1)
    y, x = np.histogram(latency, bins)
    x = (x[:-1] + x[1:])/2
    
    plt.plot(x, y, '.-')
    #y = plt.hist(latency, bins=np.arange(0.5, 40.5, 1),
    #         rwidth=0.85, histtype='step')
plt.grid(axis='y', alpha=1)
plt.grid(axis='x', alpha=1)
plt.xlabel('Latency, ms')
plt.ylabel('Counts')
plt.ylim([0,600])
plt.xlim([0,40])
    #plt.title('TBS Tracer')
    #plt.text(6.5, 18, text)

plt.legend(legend)
plt.show()



