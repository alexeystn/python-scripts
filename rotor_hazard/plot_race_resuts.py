import json
import os
import datetime
import numpy as np
from matplotlib import pyplot as plt

# 1. Export RotorHazard database to JSON (Friendly, All)

filename = '20240611.json'


def recursive_print(js, tab):
    if type(js) is dict:
        for k in js.keys():
            print('  '*tab + k)
            recursive_print(js[k], tab+1)
    if type(js) is list:
        print('  '*tab + '[0]')
        if len(js) > 0:
            recursive_print(js[0], tab+1)


def to_datetime(s):
    dt = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
    return dt


with open(filename, 'r') as f:
    j = json.loads(f.read())

# recursive_print(j, 0)

today = to_datetime(j['heats']['1']['rounds'][0]['start_time_formatted']).date()
today_ts = datetime.datetime(today.year, today.month, today.day).timestamp()
today_ts = float(today_ts)

x_hours = np.arange(19.25, 21.5, 1/4)
x_labels = ['{0}:{1:02.0f}'.format(int(x), (x - int(x))*60) for x in x_hours]
x_ticks = x_hours * 60 * 60 + today_ts

pilots = [p['callsign'] for p in j['event_leaderboard']['by_fastest_lap']]

result = {p: {'x': [], 'y': []} for p in pilots}

for heat in ['1', '2']:
    rounds = j['heats'][heat]['rounds']
    for rnd in rounds:
        rnd_time_stamp = float(to_datetime(rnd['start_time_formatted']).timestamp())
        nodes = rnd['nodes']
        for node in nodes:
            pilot = node['callsign']
            for lap in node['laps'][1:]:
                lap_time = float(lap['lap_time']) / 1000
                lap_time_stamp = rnd_time_stamp + float(lap['lap_time_stamp']) / 1000
                if not lap['deleted']:  # and lap_time > lap_time_threshold:
                    result[pilot]['x'].append(lap_time_stamp)
                    result[pilot]['y'].append(lap_time)

for p in pilots:
    print('{0:20s} {1}'.format(p, len(result[p]['x'])))

path = 'output'
if not os.path.isdir(path):
    os.mkdir(path)

plt.figure(figsize=(12, 5))

for pilot in result:

    plt.cla()
    plt.plot(result[pilot]['x'], result[pilot]['y'], 'ok', markersize=4)
    plt.gca().set_xticks(x_ticks)
    plt.gca().set_xticklabels(x_labels, rotation=30)
    plt.xlim(min(x_ticks), max(x_ticks))
    plt.ylim(0, 90)

    plt.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.ylabel('Lap time, s')
    plt.title(pilot + '   ' + today.strftime('%Y-%m-%d'))

    fig_filename = today.strftime('%Y%m%d') + ' {0}.png'.format(pilot)
    plt.savefig(os.path.join(path, fig_filename))

plt.close()
