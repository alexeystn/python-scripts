from datetime import datetime
import sqlite3
import json
import numpy as np
from matplotlib import pyplot as plt

# Load database
filename = 'database.db'
conn = sqlite3.connect(filename)
cursor = conn.cursor()

# Smoothing filter
fir_length = 5
fir = np.cos((np.linspace(-1, 1, fir_length)*np.pi))/2 + 0.5
fir /= np.sum(fir)

with open('projects.json', 'r') as f:
    project_names = json.load(f)

# Prepare X-axis
timeline_start = datetime.timestamp(datetime(2022, 12, 2))
timeline_stop = datetime.timestamp(datetime.now())
timeline_days_count = (timeline_stop - timeline_start) // (24 * 60 * 60) + 2
timeline = np.arange(timeline_days_count) * 24 * 60 * 60 + timeline_start

# Prepare Y-axis
price_change = {prj: {'change': np.zeros(timeline.shape),
                      'count': np.zeros(timeline.shape, dtype='int')}
                for prj in project_names.keys()}

fig, ax = plt.subplots()

for prj in project_names.keys():

    # Get full list of all flats
    q = "SELECT DISTINCT flat_id FROM flats WHERE project = '{0}'".format(prj)
    flat_ids = np.array(cursor.execute(q).fetchall())
    flat_ids = np.sort(flat_ids, axis=0).flatten()

    for flat_id in flat_ids:

        q = """SELECT timestamp, price FROM flats
               WHERE flat_id = {0}""".format(flat_id)
        res = cursor.execute(q).fetchall()
        res = np.array(res, dtype='int')
        time_real = res[:, 0]
        price_real = res[:, 1]
        price_interp = np.interp(timeline, time_real, price_real)
        # Get daily relative price change:
        price_interp_diff = price_interp[1:] / price_interp[:-1] - 1

        # Count only days when flat was available
        mask = np.where((timeline > time_real[0]) *
                        (timeline < time_real[-1]))[0]
        if len(mask) == 0:
            continue

        price_change[prj]['change'][mask] += price_interp_diff[mask]
        price_change[prj]['count'][mask] += 1

    # Avoid division by zero
    price_change[prj]['count'][price_change[prj]['count'] == 0] = 1

    price_change[prj]['change'] *= 100
    price_change[prj]['change'] /= price_change[prj]['count']
    price_change[prj]['sum'] = np.cumsum(price_change[prj]['change'])

    plt.plot(timeline, price_change[prj]['sum'], '-')

plt.grid(True)
plt.xlabel('Days')
plt.ylabel('Change, %')
plt.ylim(-6, 10)
xmin, xmax, ymin, ymax = plt.axis()
plt.yticks(np.arange(ymin, ymax+1))
plt.legend(project_names.values())

plt.xticks(timeline[::7],
           [datetime.fromtimestamp(dt).strftime('%d %b')
            for dt in timeline[::7]],
           rotation=45)

fig.savefig('output/trends.png', dpi=300)
plt.show()
