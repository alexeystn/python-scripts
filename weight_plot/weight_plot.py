import json
import sys
import os
import numpy as np
import matplotlib
from datetime import datetime, timedelta
from matplotlib import pyplot as plt


weight = []
dates = []

# example:
# 25.03   85.1
# 26.03   84.7

with open('data.txt', 'r') as f:
    for line in f:
        if len(line) < 12:
            continue
        line_split = line.strip().split()
        w = float(line_split[1])
        line_split_0 = line_split[0].split(sep='.')
        day = int(line_split_0[0])
        month = int(line_split_0[1])
        dt = datetime.timestamp(datetime(2023, month, day))
        weight.append(w)
        dates.append(dt)

plt.figure(figsize=(10,6))

plt.plot(dates, weight, '-')
plt.ylim((85, 110))

xmin, xmax, _, _ = plt.axis()

timestamp_ticks = np.arange(xmin, xmax, 7*24*60*60) #* (24*60*60)
timestamp_labels = [datetime.fromtimestamp(t).strftime('%d %b')
                        for t in timestamp_ticks]


plt.xticks(timestamp_ticks, rotation=45)
plt.gca().set_xticklabels(timestamp_labels)

plt.grid(True)
plt.show()





