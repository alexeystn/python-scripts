from matplotlib import pyplot as plt
import numpy as np


# Conversion: '1:05:00' -> 75
def str_to_int(s):
    return float(s)
    if ':' in s:
        s = [int(s) for s in s.split(':')]
        return s[0] * 60 + s[1]
    else:
        return 0


lap_change = 25  # 25 or 50

# Load lap times
lap_times = [[] for i in range(4)]
with open('laps.txt', 'r') as f:
    for line in f:
        line = line[:-1].split('\t')
        for i in range(4):
            t = str_to_int(line[i])
            #if t:
            lap_times[i].append(t)

# Load team names
teams = []
with open('teams.txt', 'r') as f:
    for line in f:
        teams.append(line.strip())

# Build reference line
total_laps = lap_change * 2
winner_time = np.min([t[-1] for t in lap_times if len(t) == total_laps + 1])
mid_y = np.arange(total_laps + 1)
mid_x = np.linspace(lap_times[0][0], winner_time, total_laps + 1)

# Prepare Y-axis data
y = [np.arange(len(xi)) - np.interp(xi, mid_x, mid_y) for xi in lap_times]
x = lap_times

# Draw results 1
plt.figure(figsize=(8, 5))
colors = ['r', 'y', 'g', 'b']
for i in range(4):  # Lines
    plt.plot(x[i], y[i], color=colors[i])
for i in range(4):  # Dotted line
    plt.plot(x[i][lap_change:lap_change + 2], y[i][lap_change:lap_change + 2], ':w')
for i in range(4):  # Circle markers
    for j in [lap_change, lap_change + 1]:
        plt.plot(x[i][j], y[i][j], 'o', color=colors[i], markersize=5)
plt.legend(teams)
plt.xlabel('Seconds')
plt.ylabel('Laps')
plt.grid(True)
plt.savefig('output1.png')
plt.show()


y = [np.diff(yi) for yi in lap_times]
x = np.arange(len(y[0]))+1

# Draw results 2
plt.figure(figsize=(8, 5))
colors = ['r', 'y', 'g', 'b']
for i in range(4):  # Lines
    plt.plot(x, y[i], color=colors[i])
plt.legend(teams)
plt.xlabel('Seconds')
plt.ylabel('Laps')
plt.grid(True)
plt.savefig('output2.png')
plt.show()





