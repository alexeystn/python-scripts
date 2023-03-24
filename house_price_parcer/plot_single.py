from datetime import datetime
import sqlite3
import numpy as np
from matplotlib import pyplot as plt

# Load database
filename = 'database.db'
conn = sqlite3.connect(filename)
cursor = conn.cursor()

project = 'alt53'

# Prepare X-axis
timeline_start = datetime.timestamp(datetime(2022, 12, 2))
timeline_stop = datetime.timestamp(datetime.now())
timeline_days_count = (timeline_stop - timeline_start) // (24 * 60 * 60) + 2
timeline = np.arange(timeline_days_count) * 24 * 60 * 60 + timeline_start

# Get full list of all flats
q = "SELECT DISTINCT flat_id FROM flats WHERE project = '{0}'".format(project)
flat_ids = np.array(cursor.execute(q).fetchall())
flat_ids = np.sort(flat_ids, axis=0).flatten()

q = "SELECT price FROM flats WHERE project = '{0}'".format(project)
prices = np.array(cursor.execute(q).fetchall())
print(prices.min(), prices.max())


for flat_id in flat_ids:
    q = """SELECT timestamp, price FROM flats
           WHERE flat_id = {0}""".format(flat_id)
    res = cursor.execute(q).fetchall()
    res = np.array(res, dtype='int')
    time_real = res[:, 0]
    price_real = res[:, 1]

    plt.plot(time_real, price_real/1000)
    plt.grid(True)
    plt.xlabel('Days')
    plt.ylabel('Price')

    y_mean = np.mean(price_real / 1000)

    plt.ylim(y_mean - 300, y_mean + 300)

    plt.xticks(timeline[::7],
               [datetime.fromtimestamp(dt).strftime('%d %b')
                for dt in timeline[::7]],
               rotation=45)

    plt.savefig('output/single_{0}.png'.format(flat_id), dpi=150)
    plt.close()
