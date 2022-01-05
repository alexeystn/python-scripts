import numpy as np
from matplotlib import pyplot as plt

filename = 'capture.npz'
data = np.load(filename)
timestamps = data['timestamps']
capture = data['capture']
channel = capture[:,6].astype('int')*256 + capture[:,5]
channel = (channel - 1024) / 1024 * 100
timestamps = timestamps - timestamps[0]
#timestamps = timestamps - 3.2

timestamps = timestamps - 4.5

plt.plot(timestamps, channel,'-')

plt.grid(True);
plt.xlim([0,0.8])
plt.ylim([-100,100])
plt.xlabel('Time, seconds')
plt.ylabel('Roll, %')
plt.show()
