import numpy as np
import sqlite3


class Database:

    filename = 'database.db'

    def __init__(self):
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()

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

    def save_changes(self):
        self.conn.commit()


db = Database()

print(db.get_records_count())
db.find_and_remove_errors(verbose=True)
print(db.get_records_count())
db.save_changes()
