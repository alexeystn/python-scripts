import numpy as np
from matplotlib import pyplot as plt

def constrain(n, min_n, max_n):
    if n < min_n:
        return min_n
    elif n > max_n:
        return max_n
    else:
        return n

def angle_rate(com, rate, expo, srate):
    if expo:
        com = com**4 * expo + com * (1 - expo)
    if rate > 2:
        rate = rate + 14.54 * (rate - 2)
    angle = 200 * rate * com
    if srate:
        factor = 1 / (constrain(1 - (com * srate), 0.01, 1))
        angle *= factor
    return constrain(angle, 0, 2000)

n = 500
commands = np.linspace(0, 1, n)
output = np.zeros((n, 1))

for i,c in enumerate(commands):
    output[i] = angle_rate(c, rate=0.5, expo=0, srate=0.85)
plt.plot(output)

for i,c in enumerate(commands):
    output[i] = angle_rate(c, rate=0.5, expo=0, srate=0.75)
plt.plot(output)

for i,c in enumerate(commands):
    output[i] = angle_rate(c, rate=0.4, expo=0, srate=0.75)
plt.plot(output)

plt.xlim((0, n))
plt.ylim((0, 700))
plt.grid(True)
plt.show()
