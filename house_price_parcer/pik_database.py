import os
import sqlite3
from datetime import datetime
import numpy as np


class Database:

    filename = 'database.db'
    timestamp_margin = 300

    def __init__(self):

        need_to_initialize = False
        if os.path.isfile(self.filename):
            print('Database found')
        else:
            need_to_initialize = True
            print('Database not found')
            print('Creating new database')

        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()

        if need_to_initialize:
            self.cursor.execute('''
                      CREATE TABLE IF NOT EXISTS flats
                      ([record_id] INTEGER PRIMARY KEY,
                      [project] TEXT,
                      [flat_id] INTEGER,
                      [price] INTEGER,
                      [timestamp] INTEGER
                      )
                      ''')
            self.save_changes()

    def write(self, project, flat_id, price):
        timestamp = int(datetime.timestamp(datetime.now()))
        self.cursor.execute('''
                            INSERT INTO flats (project, flat_id, price, timestamp)
                            VALUES('{0}',{1},{2},{3});
                            '''.format(project, flat_id, price, timestamp))

    def save_changes(self):
        self.conn.commit()

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
        return ret

    def get_most_exposed_flats(self, project):
        q = """
        SELECT flat_id, COUNT(flat_id) 
        FROM flats 
        WHERE project='{0}'
        GROUP BY flat_id
        ORDER BY COUNT(flat_id) DESC
        LIMIT 2;
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

    def get_records_count(self):
        q = """
        SELECT COUNT (*) 
        FROM flats
        """
        res = self.cursor.execute(q).fetchall()
        return res[0][0]

    def find_and_remove_errors(self, verbose=True):
        q = """
        SELECT DISTINCT flat_id 
        FROM flats
        """
        res = self.cursor.execute(q).fetchall()
        flat_ids = np.sort(np.array(res), axis=0).flatten()

        for flat_id in flat_ids:
            q = """
            SELECT project, COUNT(*)
            FROM flats
            WHERE flat_id = {0}
            GROUP BY project
            """.format(flat_id)
            res = dict(self.cursor.execute(q).fetchall())
            if len(res) > 1:
                if verbose:
                    print(flat_id, res)
                for prj in res:
                    if res[prj] == 1:  # remove error
                        q = """
                        DELETE FROM flats
                        WHERE flat_id = {0} 
                        AND project = '{1}'
                        """.format(flat_id, prj)
                        self.cursor.execute(q)

    def get_flat_id_list(self, project):

        q = """SELECT DISTINCT flat_id 
        FROM flats 
        WHERE project = '{0}'""".format(project)
        flat_ids = np.array(self.cursor.execute(q).fetchall())
        flat_ids = np.sort(flat_ids, axis=0).flatten()
        return flat_ids

    def get_price_and_ts(self, flat_id):
        q = """SELECT timestamp, price FROM flats
               WHERE flat_id = {0}""".format(flat_id)
        res = self.cursor.execute(q).fetchall()
        res = np.array(res, dtype='int')
        time_real = res[:, 0]
        price_real = res[:, 1]
        return time_real, price_real

    def clear_after_date(self, year, month, day):
        end_timestamp = datetime.timestamp(datetime(year, month, day))
        q = """
            DELETE FROM flats
            WHERE timestamp > {0}
            """.format(int(end_timestamp))
        self.cursor.execute(q)
