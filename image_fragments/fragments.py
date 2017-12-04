from PIL import Image, ImageFont, ImageDraw, ImageEnhance


if 0:
    start_lens_mark = -4
    start_number = 1017
    box_position = [ (500, 930),   (110, 2580), (2200, 1720), (2520, 3200), (3880, 1100), (4120, 2860)   ]
    box_title    = [ 'Left-Top', 'Left-Bottom',     'Center',     'Bottom',  'Right-Top', 'Right-Bottom' ]
else:
    start_lens_mark = -4
    start_number = 1026
    box_position = [ (980, 220),  (900, 2900),  (2430, 1880), (2420, 3320), (4240, 480), (4250, 3220)  ]
    box_title    = [ 'Left-Top', 'Left-Bottom',     'Center',   'Bottom',  'Right-Top', 'Right-Bottom' ]


box_size = (200, 100)
num = 9
spacing = 40
left_margin = 80
top_margin = 30


x = len(box_position)*(box_size[0] + spacing) + left_margin + spacing
y = num*(box_size[1] + spacing) + spacing + top_margin
im_table = Image.new('RGBA',(x, y), color = 'black')


for n in range (0, num):
    filename = './images/YDXJ' + str(start_number + n) + '.jpg'
    im_photo = Image.open(filename)
    for b in range (0, len(box_position)):
        x1 = box_position[b][0] - box_size[0] / 2
        y1 = box_position[b][1] - box_size[1] / 2
        x2 = box_position[b][0] + box_size[0] / 2
        y2 = box_position[b][1] + box_size[1] / 2
        box = (x1, y1, x2, y2)
        im_fragment = im_photo.crop(box)
        enhancer = ImageEnhance.Brightness(im_fragment)
        im_fragment = enhancer.enhance(1.2)
        x = spacing + b*(box_size[0] + spacing) + left_margin
        y = spacing + n*(box_size[1] + spacing) + top_margin
        im_table.paste(im_fragment, (x,y))
    im_photo.close()
    print(filename)


d = ImageDraw.Draw(im_table)

fnt = ImageFont.truetype('Arial', 40)
for n in range (0, num):
    x = (left_margin + spacing) / 2 
    y = spacing * (n+1) + box_size[1]*(n+1/2) + top_margin
    m = n + start_lens_mark
    txt = str(m)
    if m > 0:
        txt = '+'+txt
    w, h = d.textsize(txt, fnt)
    d.text((x-w/2,y-h/2), txt, font=fnt, fill='white')
    
fnt = ImageFont.truetype('Arial', 24)
for b in range (0, len(box_position)):
    txt = box_title[b]
    w, h = d.textsize(txt, fnt)
    x = left_margin + (b + 1/2)*box_size[0] + (b + 1)*spacing
    y = (spacing + top_margin) / 2
    d.text((x-w/2,y-h/2), txt, font=fnt, fill='white')


im_table.save('output.png')
im_table.show()

