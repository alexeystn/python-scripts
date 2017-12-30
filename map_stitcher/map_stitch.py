import cv2
import numpy
import math
import requests
from io import BytesIO
from PIL import Image



def filename(x, y, suffix):
    path = './images/'
    name = 'y{:02d}_x{:02d}'.format(y, x)
    if suffix != '':
        name += '_' + suffix
    return (path + name + '.png')


def download_map(lat, lon, zoom, res, filename):
    f = open('key.txt')
    key = f.readline()[:-1]
    url = 'https://maps.googleapis.com/maps/api/staticmap?'
    url += 'maptype=satellite'
    url += '&center=' + str(lat) + ',' + str(lon)
    url += '&zoom=' + str(zoom)
    url += '&size=' + str(res) + 'x' + str(res)
    url += '&key=' + key
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    im = im.convert("RGBA")
    im.save(filename);


def convolve_2d(im0, im1): # 0 small, 1 large
    num_white_pixels = 0
    for y0 in range(im0.shape[0]):
        for x0 in range(im0.shape[1]):
            if im0[y0,x0]:
                num_white_pixels += 1
    w = im1.shape[1] - im0.shape[1]
    h = im1.shape[0] - im0.shape[0]
    conv = numpy.zeros((h,w))
    step = 1;
    for y1 in range(h):
        for x1 in range(w):
            for y0 in range(0,im0.shape[0],step):
                for x0 in range(0,im0.shape[1],step):
                    if im0[y0,x0] & im1[y0+y1,x0+x1]:
                        conv[y1,x1] += 1

            conv[y1, x1] /= num_white_pixels / (step**2)
        # print(y1)
    x = conv.argmax() % w
    y = conv.argmax() // w
    # print(conv.max())
    return (y, x)




def calculate_shift(img0, img1, possible_overlay, part_of_edge, tolerance):
    vertical = 1 
    if vertical:
        img0_y0 = round( img0.shape[0]*(1-possible_overlay + tolerance ) )
        img0_y1 = round( img0.shape[0]*(1 - tolerance ) ) - 1
        img0_x0 = round( img0.shape[1]*( 0.5 - part_of_edge/2 + tolerance ) )
        img0_x1 = round( img0.shape[1]*( 0.5 + part_of_edge/2 - tolerance  ) ) - 1
        img1_y0 = 0
        img1_y1 = round( img1.shape[0]*(possible_overlay) ) - 1
        img1_x0 = round( img1.shape[1]*( 0.5 - part_of_edge/2 ) )
        img1_x1 = round( img1.shape[1]*( 0.5 + part_of_edge/2 )) - 1
    else:
        img0_x0 = round( img0.shape[1]*(1-possible_overlay + tolerance ) )
        img0_x1 = round( img0.shape[1]*(1 - tolerance ) ) - 1
        img0_y0 = round( img0.shape[0]*( 0.5 - part_of_edge/2 + tolerance ) )
        img0_y1 = round( img0.shape[0]*( 0.5 + part_of_edge/2 - tolerance  ) ) - 1
        img1_x0 = 0
        img1_x1 = round( img1.shape[1]*(possible_overlay) ) - 1
        img1_y0 = round( img1.shape[0]*( 0.5 - part_of_edge/2 ) )
        img1_y1 = round( img1.shape[0]*( 0.5 + part_of_edge/2 )) - 1        




    img0_part = img0[img0_y0:img0_y1, img0_x0:img0_x1]
    img1_part = img1[img1_y0:img1_y1, img1_x0:img1_x1]

    c = convolve_2d(img0_part, img1_part)

    y_shift = img0_y0 - c[0] - img1_y0
    x_shift = img0_x0 - c[1] - img1_x0
    return(y_shift, x_shift)


def image_shift(file_left, file_right):

    possible_overlay = 0.1
    part_of_edge = 0.25 # horizontal
    part_of_edge = 0.05 # vertical
    tolerance = 0.01
    img0 = cv2.imread(file_left, 0)
    img1 = cv2.imread(file_right, 0)
    img0 = cv2.Canny(img0, 150, 200)
    img1 = cv2.Canny(img1, 150, 200)
    # cv2.imwrite('edges.png', img1)
    return calculate_shift(img0, img1, possible_overlay, part_of_edge, tolerance)
    

zoom = 16
lat = 55.842922
lon = 37.512847
res = 640

x_steps = 5
y_steps = 5

meters_per_pixel = 156543.03392 * math.cos(lat * math.pi / 180) / (2**zoom)
degrees_per_pixel_lon = meters_per_pixel / 1000 / 111.11 / math.cos(lat * math.pi / 180)
degrees_per_pixel_lat = meters_per_pixel / 1000 / 111.11
lon_step = degrees_per_pixel_lon * res * 0.9
lat_step = degrees_per_pixel_lat * res * 0.9


if 0: # download map
    for x in range(x_steps):
        for y in range(y_steps):
            download_map(lat-lat_step*y, lon+lon_step*x, zoom, res, filename(x, y, ''))
            print(x, y)

if 0: # stitch horizontally
    x_pos = [0 for i in range(x_steps)]
    y_pos = [0 for i in range(x_steps)]
    y = 4
    for xi in range(x_steps-1):
        file_left = filename(xi, y, '')
        file_right = filename(xi+1, y, '')
        s = image_shift(file_left, file_right)
        x_pos[xi+1] = x_pos[xi] + s[1]
        y_pos[xi+1] = y_pos[xi] + s[0]
    print(x_pos)
    print(y_pos)        
    width = max(x_pos) + res
    height = max(y_pos) + res
    stitched_image = numpy.zeros((height,width,3), numpy.uint8)
    for xi in range(x_steps):
        img = cv2.imread(filename(xi, y, ''))
        stitched_image[y_pos[xi]:y_pos[xi]+img.shape[0], x_pos[xi]:x_pos[xi]+img.shape[1], :] = img
    cv2.imwrite('./images/stitched_' + str(y) +'.png',stitched_image)    


if 1: # stitch vertically
    x_pos = [0 for i in range(y_steps)]
    y_pos = [0 for i in range(y_steps)]
    for yi in range(y_steps-1):
        file_top = './images/stitched_' + str(yi) +'.png'
        file_bottom = './images/stitched_' + str(yi+1) +'.png'
        s = image_shift(file_top, file_bottom)
        x_pos[yi+1] = x_pos[yi] + s[1]
        y_pos[yi+1] = y_pos[yi] + s[0]
        print(yi)
    print(x_pos)
    print(y_pos)


    img = cv2.imread('./images/stitched_0.png')


    width = max(x_pos) + img.shape[1]
    height = max(y_pos) + img.shape[0]
    stitched_image = numpy.zeros((height,width,3), numpy.uint8)
    for yi in range(y_steps):
        img = cv2.imread('./images/stitched_' + str(yi) +'.png')
        stitched_image[y_pos[yi]:y_pos[yi]+img.shape[0], x_pos[yi]:x_pos[yi]+img.shape[1], :] = img
    cv2.imwrite('full.png',stitched_image)    







print('Done')




