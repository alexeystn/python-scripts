from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import calendar
import xlrd

# read dates from xlsx file
rb = xlrd.open_workbook('../Batteries.xlsx')
sheet = rb.sheet_by_index(0)
d_1900_1970 = 25569 - 365 - 1

flights = []
for r in range(2,120):
    val = sheet.row_values(r)[0]
    try:
        d = datetime.fromordinal(int(val)-d_1900_1970)
    except:
        break
    day = d.day
    month = d.month
    year = d.year + 1970 - 2
    flights.append([year, month, day])

# initial parameters
scale = 10
day_font_size = scale*2
year_font_size = scale*4
month_font_size = int(scale*2.5)
row_spacing = scale*3
col_spacing = scale*3
title_spacing = scale*5
margin = scale*7
month_spacing = scale*5
year_spacing = scale*5
image_width = margin*2 + col_spacing*5*3 + month_spacing*2
image_height = margin*2 + row_spacing*6*4 + title_spacing*4 \
               + month_spacing*3 + year_spacing
font_name = 'Helvetica'

for c_year in [2016, 2017]:
    img = Image.new('RGBA',(image_width, image_height), color = 'white')
    drw = ImageDraw.Draw(img)
    for c_month in range(0,12):
        x_pos = c_month % 3
        y_pos = c_month // 3
        c_month += 1
        cal = calendar.monthcalendar(c_year, c_month)
        x_month = x_pos*(5*col_spacing + month_spacing) + margin
        y_month = y_pos*(6*row_spacing + month_spacing + title_spacing) \
                  + margin + year_spacing
        x_shift = 0
        if len(cal) == 5:
            x_shift = col_spacing/2
        # days table
        fnt = ImageFont.truetype(font_name, day_font_size)
        for wk in range(0, len(cal)):
            for wd in range(0, 7):
                day = cal[wk][wd]
                if day:
                    txt = str(day)
                else:
                    txt = ''
                w, h = drw.textsize(txt, fnt)
                x = wk*col_spacing + x_month + x_shift
                y = wd*row_spacing + y_month + row_spacing*1.5
                if [ c_year, c_month, day ] in flights:
                    col = 'black'
                    rect = (x - col_spacing/2, y - row_spacing/2, \
                            x + col_spacing/2, y + row_spacing/2)
                    drw.rectangle(rect, fill='lightpink', outline=None)
                else:
                    col = 'black'
                drw.text((x-w/2,y-h/2), txt, font=fnt, fill=col)
        # month title
        txt = calendar.month_name[c_month]
        fnt = ImageFont.truetype(font_name, month_font_size)
        w, h = drw.textsize(txt, fnt)
        x = 2.5*col_spacing + x_month
        y = y_month
        drw.text((x-w/2,y-h/2), txt, font=fnt, fill='grey')
        
    # year title
    fnt = ImageFont.truetype(font_name, year_font_size)
    txt = str(c_year)
    w, h = drw.textsize(txt, fnt)
    x = img.width/2
    y = (year_spacing + margin) / 2
    drw.text((x-w/2,y-h/2), txt, font=fnt, fill='black')
        
    img.save('calendar_' + str(c_year) + '.png')





