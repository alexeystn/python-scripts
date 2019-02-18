import xlrd
from matplotlib import pyplot as plt
import calendar as cal
import numpy as np

def diagram1(values, labels, title):
    fig = plt.figure(figsize = (5, len(labels)/4))
    ax = fig.subplots()
    ax.set_frame_on(False)
    pos = np.arange(len(labels))
    ax.barh(pos, values, align='center', color='grey')
    ax.tick_params(length=0)
    ax.set_yticks(pos)
    ax.set_xticks([])
    ax.set_yticklabels(labels)
    for i in pos:
        ax.text(values[i], i, ' %d ' % values[i], ha='left', va='center')
    ax.set_xlim((0, np.asarray(values).max()*1.1))
    ax.invert_yaxis()
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def diagram2(values, labels, title):
    fig = plt.figure(figsize = (5, len(labels)/6))
    ax = fig.subplots()
    ax.set_frame_on(False)
    pos = np.arange(len(labels))
    ax.barh(pos, values, align='center', color='grey')
    ax.tick_params(length=0)
    ax.set_yticks(pos)
    ax.set_xticks([])
    ax.set_yticklabels(labels)
    for i in pos:
        ax.text(values[i], i, ' %d ' % values[i], ha='left', va='center')
    ax.set_xlim((0, np.asarray(values).max()*1.1))
    ax.invert_yaxis()
    ax.set_title(title)
    plt.tight_layout()
    plt.show()
    

import os

print( os.path.abspath("expense_stats.txt"))


rb = xlrd.open_workbook('/Users/imac/Documents/Финансы/Expense/Expense.xlsx')
sheet = rb.sheet_by_name('Expense')



titles = ['Year', 'Month', 'Day', 'Amount', 'Category', 'Subcategory', 'Comment']

categories = {}

for i in range(1, sheet.nrows):
    cat = sheet.cell_value(i, titles.index('Category'))
    sub = sheet.cell_value(i, titles.index('Subcategory'))
    if not cat in categories.keys():
        categories[cat] = {}
    if not sub in categories[cat]:
        categories[cat][sub] = 1
    else:
        categories[cat][sub] += 1
    
k = list(categories.keys())
k.sort()
for key in k:
    print(key +':')
    ss = list(categories[key].keys())
    ss.sort()
    for s in ss:
        print('  ' + s + ' - ' + str( categories[key][s]))





##year_start = 2017
##year_stop = 2019
##
##expense = {y: {(m+1): 0 for m in range(12)} for y in range(year_start, year_stop)}
##
##if 1:
##    rb = xlrd.open_workbook('Archive.xlsx')
##    sheet = rb.sheet_by_name('Expense')
##
##    titles = ['Year', 'Month', 'Day', 'Amount', 'Category', 'Subcategory', 'Comment']
##
##    expense = {y: {(m+1): 0 for m in range(12)} for y in range(year_start, year_stop)}
##
##    ind = titles.index('Year')
##    for i in range(1, sheet.nrows):
##        val = sheet.cell_value(i, ind)
##        year = sheet.cell_value(i, titles.index('Year'))
##        month = sheet.cell_value(i, titles.index('Month'))
##        category = sheet.cell_value(i, titles.index('Category'))
##        amount = sheet.cell_value(i, titles.index('Amount'))
##        if category == 'RC Hobby' or category == 'RC hobby':
##            try:
##                expense[year][month] += amount
##            except:
##                amount = 0
##        
##x_tick = []
##y_expenses = []
##
##for y in range(year_start, year_stop):
##    for m in range(12):
##        y_expenses.append(expense[y][m+1])
##        if m == 0:
##            x_tick.append(str(y) + ' ' + cal.month_name[m+1][:3])
##        else: 
##            x_tick.append(cal.month_name[m+1][:3])
##
##
##
##diagram1(y_expenses, x_tick, 'Expense')

    


