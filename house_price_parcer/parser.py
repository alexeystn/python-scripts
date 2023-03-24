import re
import os
from datetime import datetime
import sqlite3
import json


class Database:

    filename = 'database.db'

    def __init__(self):
        if os.path.isfile(self.filename):
            return
        conn = sqlite3.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute('''
                  CREATE TABLE IF NOT EXISTS flats
                  ([record_id] INTEGER PRIMARY KEY,
                  [project] TEXT,
                  [flat_id] INTEGER,
                  [price] INTEGER,
                  [timestamp] INTEGER
                  )
                  ''')
        conn.commit()

    def write(self, project, id_price_pairs):
        timestamp = int(datetime.timestamp(datetime.now()))
        conn = sqlite3.connect(self.filename)
        cursor = conn.cursor()
        for id_price in id_price_pairs:
            cursor.execute('''
                      INSERT INTO flats (project, flat_id, price, timestamp)
                      VALUES('{0}',{1},{2},{3});
                      '''.format(project, id_price[0], id_price[1], timestamp))
        conn.commit()


class Parser:

    filename = 'temp.html'
    project = ''

    def download_html(self):
        url = 'https://old.pik.ru/search/{0}'.format(self.project) +\
              '?rooms=1,2&areaFrom=35&sortBy=price'
        command = 'curl "{0}" -o {1} -k'.format(url, self.filename)
        print(command)
        os.system(command)

    def get_id_price_pairs(self):
        with open(self.filename, 'r', encoding="utf-8") as f:
            for line in f:
                if len(line) > 1e6:
                    break

        id_price_pairs = []

        p_price = re.compile(r'от \d{1,2} \d{3} \d{3}')
        p_id = re.compile(r'data-id="\d{6}"')

        for m_id, m_price in zip(p_id.finditer(line), p_price.finditer(line)):
            int_id = int(m_id.group()[9:-1])
            int_price = int(''.join((m_price.group()[3:].split())))
            id_price_pairs.append((int_id, int_price))
            print(int_id, int_price)

        return id_price_pairs

    def archive(self):
        new_filename = './archive/'
        new_filename += datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename += '_' + self.project + '.html'
        os.rename(self.filename, new_filename)


def load_project_list():

    with open('projects.json', 'r') as f:
        data = json.load(f)
        print(data)
        return list(data.keys())


db = Database()
projects = load_project_list()

p = Parser()

for pr in projects:
    p.project = pr
    p.download_html()
    pairs = p.get_id_price_pairs()
    db.write(pr, pairs)
    p.archive()

