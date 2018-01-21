import numpy as np
import csv
import math
import matplotlib.pyplot as plt

def nameform_string(nameform):
    s = '('
    for i in range(len(nameform)-2):
        s += nameform[i+1] + ','
    s += nameform[-1] + ')'
    return s

names = {} # {'Alex': 7, 'Andrew': 6, ... }
years = {} # {2000: 125, 2001: 432, ... }
messages = [] # number of written messages

for year in range(2000, 2019):
    years[year] = [0 for i in range(12)]

# Load nameforms
nameforms = []
f = open('forms.txt', 'r', encoding='utf-8')
for line in f:
    form = line[:-1].split(sep=',')
    nameforms.append(form)
    names[form[0]] = 0
f.close()

# Load women
women = []
f = open('women.txt', 'r', encoding='utf-8')
for line in f:
    woman = line[:-1]
    women.append(woman)
f.close()


# Field positions in csv
index_nickname = 0
index_reg_date = 1
index_msg_num  = 2
index_1st_name = 3
index_2nd_name = 4
index_name = index_1st_name # 1st or 2nd
name_threshold = 3 # 3 for 1st, 10 for 2nd

# Read csv database
f = open('users.csv', 'r', encoding='utf-8')
reader = csv.reader(f, delimiter='\t')
for user in reader:
    date = user[index_reg_date]
    if (date == 'Вчера') | (date == 'Сегодня'):
        date = '01.12.2017'
    year = int(date[-4:])
    month = int(date[-7:-5])-1
    years[year][month] += 1
    messages.append(int(user[index_msg_num].replace(',', '')))
    name = user[index_name].capitalize()
    if 'apedserft' in name:
        continue    
    if name in names.keys():
        names[name] += 1
    else: 
        names[name] = 1
total_num = reader.line_num


if 1: # WOMEN
    women_num = 0
    women_names = []
    for name in names.keys():
        if name in women:
            women_names.append(name)
    women_names.sort(key = None)
    for name in women_names:
        women_num += names[name]
        print('{0:11} {1:2}'.format(name + ':', names[name]))
    print('-------------')
    print('Total {0} women ({1:.3f}%)'.format(women_num, women_num/total_num*100))
     

if 0: # NAMES
    
    # Combine name forms
    for name in names.keys():
        for nameform in nameforms:
            if name in nameform:
                if name != nameform[0]:
                    if nameform[0] not in names.keys():
                        names[nameform[0]] = 0
                    names[nameform[0]] += names[name]
                    names[name] = 0

    # Sort names by quantity
    names_sorted = list(names.keys())
    names_sorted.sort(key = (lambda x: names[x]), reverse = True)

    # Display names
    frequent_names = 0
    for name in names_sorted:
        if names[name] >= name_threshold:
            percentage = names[name]/total_num*100
            print('{0:14} {1:4} {2:6.2f}%  '.
                  format(name + ':', names[name], percentage), end = '')
            frequent_names += names[name]
            for nameform in nameforms:
                if name in nameform:
                    print(nameform_string(nameform), end = '')
            print('')
    rare_names = total_num - frequent_names
    percentage = rare_names/total_num*100
    print('{0:14} {1:4} {2:6.2f}%  '.format('Другие:', rare_names, percentage))


if 0: # MESSAGES NUMBER

    # Sort 
    messages.sort(reverse = True)
    messages = np.asarray(messages)

    # Display messages
    limit = False
    for m in range(1,messages.size):
        users_percent = m / messages.size * 100
        messages_percent = messages[:m].sum() / messages.sum() * 100
        if (users_percent + messages_percent) > 100:
            if not limit:
                limit = True
                print('{:6.2f}% users: {:6.2f}% messages \n'.
                      format(users_percent, messages_percent))

    # Percentage
    percentage = []
    range_text = []
    for e in range(-1,5):
        min_limit = round(10**e)
        max_limit = round(10**(e+1) - 1)
        s = ((messages >= min_limit) & (messages <= max_limit)).sum()
        percentage.append(s)
        s = s/total_num*100
        print('{0}-{1}: {2:.1f}%'.format(min_limit, max_limit, s))
        range_text.append('{0}-{1}\n({2:.1f}%)'.format(min_limit, max_limit, s))
    print('')
    
    for e in range(-1,5):
        limit = round(10**(e+1))
        s = (messages < limit).sum()
        s = s/total_num*100
        print('m<{0}: {1:.1f}%'.format(limit, s))

    # Plot
    range_text[0] = range_text[0][2:]
    labels = range_text
    sizes = percentage
    explode = [0.05 for i in sizes]
    plt.pie(sizes, explode=explode, labels=labels, autopct=None,
            pctdistance=0.8, labeldistance=1.2, textprops={'ha':'center'})
    plt.show()

if 0: # REGISTRATION

    # Display years
    users_num = []
    for year in range(2000, 2018): 
        print(str(year) + ': ', end = '')
        print(years[year])
        users_num.extend(years[year])
    users_num = np.asarray(users_num).cumsum()
    reg_date = [ (2000 + i/12) for i in range(len(users_num)) ]
    plt.plot(reg_date, users_num)
    plt.xlabel('Year')
    plt.xticks( range(2000,2019,2), rotation=70)
    plt.xlim(2000,2018)    
    plt.ylim(0,16000)
    plt.ylabel('Users')
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
    plt.grid(True)
    plt.show()

