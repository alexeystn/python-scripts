import sqlite3
import numpy as np
from datetime import datetime


class DataBase:

    expense_categories = {}
    income_categories = {}

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.expense_categories = self.load_categories(0)
        self.income_categories = self.load_categories(1)

    def load_categories(self, key):
        result = {}
        q = "SELECT name, _id FROM category WHERE key = {0} AND id_roditel = 0 ORDER BY nom".format(key)
        res = self.cursor.execute(q).fetchall()
        for r in res:
            name = r[0]
            id_ = r[1]
            result[name] = {"id": id_, "sub": False}
            q = "SELECT name, _id FROM category WHERE key = {0} AND id_roditel = {1} ORDER BY name".\
                format(key, id_)
            res_sub = self.cursor.execute(q).fetchall()
            for r_sub in res_sub:
                name_sub = r_sub[0]
                id_sub = r_sub[1]
                result[name_sub] = {"id": id_sub, "sub": True}
        return result

    def print_categories(self, key):
        if key:
            categories = self.expense_categories
        else:
            categories = self.income_categories
        for c in categories:
            if categories[c]['sub']:
                print('    ', end='')
            print('{0:2d}: {1}'.format(categories[c]['id'], c))

    def query_category(self, category, date):
        year, month = date
        q = "SELECT summa, opis, date, id_podCat FROM rashodi"
        if self.expense_categories[category]['sub']:
            q += " WHERE id_podCat = {0}".format(self.expense_categories[category]['id'])
        else:
            q += " WHERE id_cat = {0}".format(self.expense_categories[category]['id'])
        q += " AND strftime('%Y', date(date/1000,'unixepoch')) IN('{0}')".format(year)
        q += " AND strftime('%m', date(date/1000,'unixepoch')) IN('{0:02d}')".format(month)
        q += " ORDER BY date"
        res = self.cursor.execute(q).fetchall()
        return res

    def print_report(self, category, start_date, stop_date=None, details=False, print_sub=False):

        start_year, start_month = start_date
        if stop_date:
            stop_year, stop_month = stop_date
        else:
            stop_year, stop_month = datetime.now().year, datetime.now().month

        for year in range(start_year, stop_year + 1):
            for month in range(12):
                if year == start_year and month + 1 < start_month:
                    continue
                if year == stop_year and month + 1 > stop_month:
                    break
                res = self.query_category(category, (year, month + 1))
                total = np.sum([r[0] for r in res])
                print('{0}-{1:02d}: {2:.0f}'.format(year, month + 1, total))
                if not details:
                    continue
                for r in res:
                    self.print_operation(r, print_sub)

    def category_name_by_id(self, id_):
        ret = ''
        for cat in self.expense_categories:
            if self.expense_categories[cat]['id'] == id_:
                ret = cat
                break
        return ret

    def print_operation(self, r, print_sub=False):
        amount = int(r[0])
        description = r[1]
        date = datetime.fromtimestamp(r[2] / 1000)
        sub_cat = self.category_name_by_id(r[3]) if print_sub else ''
        print(' ' * 15 + '{0}-{1:02d}-{2:02d} {3:6d}  {4} {5}'.format(date.year, date.month, date.day,
                                                                      amount, description, sub_cat))

    def print_structure(self, date, details=False):
        summary = []
        total_month = 0
        for category in self.expense_categories:
            if self.expense_categories[category]['sub']:
                continue
            res = self.query_category(category, date)
            if len(res) == 0:
                continue
            else:
                total = np.sum([r[0] for r in res])
                total_month += total
                summary.append((category, int(total)))
        summary.sort(key=lambda x: x[1], reverse=True)
        print(int(total_month))
        for s in summary:
            print('{0:6d} {1}'.format(s[1], s[0]))
            if details:
                res = self.query_category(s[0], date)
                for r in res:
                    self.print_operation(r)


db = DataBase('backup.db')
# db.print_categories(1)
db.print_report('Еда', (2022, 1), (2022, 12), details=True, print_sub=True)
# db.print_structure((2022, 1), details=0)
