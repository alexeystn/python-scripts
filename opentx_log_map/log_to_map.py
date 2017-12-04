from PIL import Image, ImageDraw, ImageColor
import nav


zoom = 16

ratio = 3

log = nav.read_log('log_dec.csv')
path = nav.path_from_log(log)


im = nav.download_map(path,zoom)
im = im.resize((im.width*ratio, im.height*ratio))

draw = ImageDraw.Draw(im)

for i in range(0, len(path['Lat'])):
    x, y = nav.coords_to_pixel(path['Lat'][i], path['Lon'][i])
    color = nav.rssi_to_color(path['Rssi'][i]) 
    rad = nav.altitude_to_radius(path['Alt'][i])
    ang = path['Angle'][i]
    x *= ratio
    y *= ratio
    rad *= ratio
    arrow = nav.arrow_polygon(x, y, ang, rad)
    draw.polygon(arrow, outline=None, fill=color)

im = im.resize((im.width//ratio, im.height//ratio), Image.ANTIALIAS)
im.save('map_output.png')
im.show()

print('Done')


