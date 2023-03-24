import numpy as np
import sqlite3
from datetime import datetime


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

    def clear_after_date(self, year, month, day):
        
        end_timestamp = datetime.timestamp(datetime(year, month, day))
        q = """
            DELETE FROM flats
            WHERE timestamp > {0}
            """.format(int(end_timestamp))
        self.cursor.execute(q)

    def save_changes(self):
        self.conn.commit()


db = Database()

print(db.get_records_count())
db.clear_after_date(2023, 2, 1)
print(db.get_records_count())
db.save_changes()
