from datetime import datetime
import sqlite3
import numpy as np
from matplotlib import pyplot as plt

class Database:

    filename = 'database.db'
    timestamp_margin = 300

    def __init__(self):
        conn = sqlite3.connect(self.filename)
        self.cursor = conn.cursor()

    def get_timestamps(self):
        q = """
        SELECT DISTINCT timestamp
        FROM flats
        """
        m = self.timestamp_margin
        res = self.cursor.execute(q).fetchall()
        unique_timestamps = list(set([r[0]//m * m for r in res]))
        unique_timestamps.sort()
        datetimes = [datetime.fromtimestamp(t) for t in unique_timestamps]
        labels = [dt.strftime('%Y-%m-%d %H:%M') for dt in datetimes]
        return unique_timestamps, labels

    def get_project_names(self):
        q = """
        SELECT DISTINCT project
        FROM flats
        """
        res = self.cursor.execute(q).fetchall()
        return [r[0] for r in res]


    def get_number_of_projects_in_sessions(self, timestamps):
        ret = [0] * len(timestamps)
        for i, timestamp in enumerate(timestamps):
            q = """
            SELECT COUNT(*) 
            FROM flats 
            WHERE timestamp BETWEEN {0} AND {1}
            """.format(timestamp, timestamp + self.timestamp_margin)
            res = self.cursor.execute(q).fetchall()
            ret[i] = res[0][0]
        return  ret


    def get_most_exposed_flats(self, project):
        q = """
        SELECT flat_id, COUNT(flat_id) 
        FROM flats 
        WHERE project='{0}'
        GROUP BY flat_id
        ORDER BY COUNT(flat_id) DESC
        LIMIT 3;
        """.format(project)
        res = self.cursor.execute(q).fetchall()
        return [r[0] for r in res]


    def get_price_change(self, flat_id):
        q = """
        SELECT price, timestamp/{0}*{0}
        FROM flats 
        WHERE flat_id='{1}'
        """.format(self.timestamp_margin, flat_id)
        res = self.cursor.execute(q).fetchall()
        prices = np.array([r[0] for r in res])
        timestamps = np.array([r[1] for r in res])
        return prices, timestamps
        
            

db = Database()
timestamps, labels = db.get_timestamps()
t0 = timestamps[0]
# print(timestamps)

counts = db.get_number_of_projects_in_sessions(timestamps)
for label, count in zip(labels, counts):
    print(label, '-', count)

legend = []

for prj in db.get_project_names():
    print(prj)
    flat_ids = db.get_most_exposed_flats(prj)
    for flat_id in flat_ids:
        prices, timestamps = db.get_price_change(flat_id)
        timestamps = (timestamps - t0)/3600/24
        
        prices = (prices/prices[0] - 1) * 100
        legend.append((prj + ' ' + str(flat_id)))
        plt.plot(timestamps, prices, '-d')

plt.legend(legend)
plt.savefig('output.png')
plt.show()
        









