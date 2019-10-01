from datetime import datetime
import calendar
import xlrd
from matplotlib import pyplot as plt

rb = xlrd.open_workbook('../../../Квадрокоптер/Batteries.xlsx')
sheet = rb.sheet_by_index(0)

stats = {}

for year in range(2016,2020):
    stats[year] = [0 for i in range(12)]

for r in range(5,150):
    
    excel_date = sheet.row_values(r)[0]
    if excel_date == '':
        break
    dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(excel_date) - 2)
    num_accums = sheet.row_values(r)[25]
    
    stats[dt.year][dt.month - 1] += int(num_accums)

labels = []
values = []

for year in stats:
    for month, num_accums in enumerate(stats[year]):
        if year == 2019 and month == 9:
            break
        s = '{0}.{1}: {2}'.format(year, calendar.month_name[month + 1], stats[year][month])
        if month == 0:
            labels.append('{0}    {1}'.format(year, calendar.month_name[month + 1]))
        else:
            labels.append(calendar.month_name[month + 1])
        values.append(stats[year][month])

x = range(0,len(values))

fig = plt.figure(figsize=(10,4))

plt.plot(x, values, marker='s')
plt.xticks(x, labels, rotation='vertical')
plt.grid(color='k', linestyle=':')
plt.tick_params(labelright=True)
fig.tight_layout()

plt.savefig('plot.png')

plt.show()


