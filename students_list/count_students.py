from docx import Document
from datetime import datetime
from calendar import monthrange

if 0:
    path = 'Таблица для приказов 1-4.docx'
    classes = (1,4)
else:
    path = 'Таблица для приказов 5-11.docx'
    classes = (5,11)

student_list = []

year = 2019
month = 11

weeks = [ [5,8], [11,15], [18,22], [25,29] ]

doc = Document(path)
for i, row in enumerate(doc.tables[0].rows[1:]):
    row_cells = row.cells

    #print(i)
    class_number = int(row_cells[3].text)
    arrival_date = row_cells[6].text
    departure_date = row_cells[7].text  
    arrival_date = datetime.strptime(arrival_date, '%d.%m.%Y')

    if len(departure_date) < 10:
        departure_date = datetime(year,month,monthrange(year,month)[1])
    else:
        departure_date = datetime.strptime(departure_date, '%d.%m.%Y')
    student_list.append( (class_number, arrival_date, departure_date) )


for week in weeks:
    
    print('{0}.{2} - {1}.{2}'.format(week[0],week[1],month))
    student_numbers = dict([(i, 0) for i in range(classes[0],classes[1]+1)])
    first_week_day = datetime(year,month,week[0])
    last_week_day = datetime(year,month,week[1])

    for st in student_list:
        class_number, arrival_date, departure_date = st
        if arrival_date <= last_week_day and departure_date >= first_week_day:
            student_numbers[class_number] += 1

    for i in student_numbers.keys():
        print(i, end='\t')
    print('')
    for i in student_numbers.keys():
        print(student_numbers[i], end='\t')
    print('')
    print('')
        



