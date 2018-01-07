import cv2
import numpy
import math
import requests
from io import BytesIO
from PIL import Image


def convolve_2d(im0, im1): # 0 small, 1 large
    num_white_pixels = 0
    for y0 in range(im0.shape[0]):
        for x0 in range(im0.shape[1]):
            if im0[y0, x0]:
                num_white_pixels += 1
    w = im1.shape[1] - im0.shape[1]
    h = im1.shape[0] - im0.shape[0]
    conv = numpy.zeros((h,w))
    step = 1;
    for y1 in range(h):
        for x1 in range(w):
            for y0 in range(0, im0.shape[0], step):
                for x0 in range(0, im0.shape[1], step):
                    if im0[y0, x0] & im1[y0 + y1, x0 + x1]:
                        conv[y1, x1] += 1
            conv[y1, x1] /= num_white_pixels / (step**2)
    x = conv.argmax() % w
    y = conv.argmax() // w
    return (y, x)


def download_map_fragment(p, lat, lon, x, y):
    url =''
    if p['provider'] == 'g': # google
        f = open('key.txt')
        key = f.readline()[:-1]
        url += 'https://maps.googleapis.com/maps/api/staticmap?'
        if p['type'] == 's': # satellite
            url += 'maptype=satellite'
        else: # map
            url += 'maptype=map'       
        url += '&center=' + str(lat) + ',' + str(lon)
        url += '&zoom=' + str(p['zoom'])
        url += '&size=' + str(p['res_x']) + 'x' + str(p['res_y'])
        url += '&key=' + key
    else: # yandex
        url += 'https://static-maps.yandex.ru/1.x/?'
        url += 'll=' + str(lon) + ',' + str(lat)
        url += '&size=' + str(p['res_x']) + ',' + str(p['res_y'])
        url += '&z=' + str(p['zoom'])
        if p['type'] == 's': # satellite
            url += '&l=sat'
        else: # map
            url += '&l=map' 
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    im = im.convert("RGBA")
    filename = p['path'] + 'y{:02d}_x{:02d}'.format(y, x) + '.png'
    im.save(filename)


def download_map(p):
    print('Download:')
    step_deg_x = p['deg/pix_x'] * p['res_x'] * (1 - p['overlap_x'])
    step_deg_y = p['deg/pix_y'] * p['res_y'] * (1 - p['overlap_y']) * math.cos(p['lat']/180*math.pi)
    for y in range(p['steps_y']):
        for x in range(p['steps_x']):
            lon = p['lon'] + step_deg_x * (x - (p['steps_x'] - 1) / 2)
            lat = p['lat'] - step_deg_y * (y - (p['steps_y'] - 1) / 2)           
            download_map_fragment(p, lat, lon, x, y)
            print('x {:02d}, y {:02d}'.format(x, y))


def relative_shift(p, filename0, filename1, direction):
    img0 = cv2.imread(filename0, 0)
    img1 = cv2.imread(filename1, 0)
    img0 = cv2.Canny(img0, 150, 200)
    img1 = cv2.Canny(img1, 150, 200)
    tolerance = 0.01
    if direction == 'v':
        overlap = p['overlap_y']
        part_of_edge = 0.25 / p['steps_x']
    if direction == 'h':
        overlap = p['overlap_x']
        part_of_edge = 0.25
    if direction == 'h':
        img0_x0 = round(img0.shape[1] * (1 - overlap + tolerance) )
        img0_x1 = round(img0.shape[1] * (1 - tolerance ) ) - 1
        img0_y0 = round(img0.shape[0] * (0.5 - part_of_edge/2 + tolerance))
        img0_y1 = round(img0.shape[0] * (0.5 + part_of_edge/2 - tolerance)) - 1
        img1_x0 = 0
        img1_x1 = round(img1.shape[1] * overlap) - 1
        img1_y0 = round(img1.shape[0] * (0.5 - part_of_edge/2))
        img1_y1 = round(img1.shape[0] * (0.5 + part_of_edge/2)) - 1
    if direction == 'v':
        img0_y0 = round(img0.shape[0] * (1 - overlap + tolerance))
        img0_y1 = round(img0.shape[0] * (1 - tolerance)) - 1
        img0_x0 = round(img0.shape[1] * ( 0.5 - part_of_edge/2 + tolerance))
        img0_x1 = round(img0.shape[1] * ( 0.5 + part_of_edge/2 - tolerance)) - 1
        img1_y0 = 0
        img1_y1 = round(img1.shape[0] * overlap) - 1
        img1_x0 = round(img1.shape[1] * (0.5 - part_of_edge/2))
        img1_x1 = round(img1.shape[1] * (0.5 + part_of_edge/2)) - 1
    img0_part = img0[img0_y0:img0_y1, img0_x0:img0_x1]
    img1_part = img1[img1_y0:img1_y1, img1_x0:img1_x1]
    c = convolve_2d(img0_part, img1_part)
    shift_y = img0_y0 - c[0] - img1_y0
    shift_x = img0_x0 - c[1] - img1_x0    
    return(shift_y, shift_x)


def stitch_horizontal(p):
    print('Stitch horizontal:')
    pos_x = [0 for i in range(p['steps_x'])]
    pos_y = [0 for i in range(p['steps_x'])]    
    for yi in range(p['steps_y']):
        print('Row ' + str(yi) + ':')
        for xi in range(p['steps_x']-1):
            filename0 = p['path'] + 'y{:02d}_x{:02d}'.format(yi, xi) + '.png'
            filename1 = p['path'] + 'y{:02d}_x{:02d}'.format(yi, xi + 1) + '.png'
            s = relative_shift(p, filename0, filename1, 'h')
            pos_x[xi+1] = pos_x[xi] + s[1]
            pos_y[xi+1] = pos_y[xi] + s[0]
        print(pos_x)
        print(pos_y)
        width = max(pos_x) + p['res_x']
        height = max(pos_y) + p['res_y']
        stitched_image = numpy.zeros((height, width, 3), numpy.uint8)
        for xi in range(p['steps_x']):
            filename = p['path'] + 'y{:02d}_x{:02d}'.format(yi, xi) + '.png'
            img = cv2.imread(filename)
            stitched_image[pos_y[xi]:(pos_y[xi] + img.shape[0]), pos_x[xi]:(pos_x[xi] + img.shape[1]), :] = img
        filename = p['path'] + 's{:02d}'.format(yi) + '.png'
        cv2.imwrite(filename, stitched_image)     


def stitch_vertical(p):
    print('Stitch vertical:')
    pos_x = [0 for i in range(p['steps_y'])]
    pos_y = [0 for i in range(p['steps_y'])]
    for yi in range(p['steps_y'] - 1):
        print('Rows ' + str(yi) + ' + ' +  str(yi))
        filename0 = p['path'] + 's{:02d}'.format(yi) + '.png'
        filename1 = p['path'] + 's{:02d}'.format(yi + 1) + '.png'
        s = relative_shift(p, filename0, filename1, 'v')
        pos_x[yi+1] = pos_x[yi] + s[1]
        pos_y[yi+1] = pos_y[yi] + s[0]
    print(pos_x)
    print(pos_y)
    filename = p['path'] + 's00' + '.png'
    img = cv2.imread(filename)
    width = max(pos_x) + img.shape[1]
    height = max(pos_y) + img.shape[0]
    stitched_image = numpy.zeros((height, width, 3), numpy.uint8)
    for yi in range(p['steps_y']):
        filename = p['path'] + 's{:02d}'.format(yi) + '.png'
        img = cv2.imread(filename)
        stitched_image[pos_y[yi]:(pos_y[yi] + img.shape[0]), pos_x[yi]:(pos_x[yi] + img.shape[1]), :] = img
    filename = p['path'] + 'map' + '.png'
    cv2.imwrite(filename, stitched_image) 


def initialize(p):
    p['path'] = './images/'
    if (p['provider'] == 'y'):
        p['res_x'] = 600
        p['res_y'] = 450
    elif (p['provider'] == 'g'): 
        p['res_x'] = 640
        p['res_y'] = 640
    else:
        print('Unknown provider')
    if (p['type'] != 'm') & (p['type'] != 's'):
        print('Unknown type')
    p['deg/pix_x'] = 360 / 256 * (1 + 1/533) * 2**(-p['zoom'])
    p['deg/pix_y'] = 360 / 256 * 2**(-p['zoom'])
    p['overlap_x'] = 0.1
    p['overlap_y'] = 0.1
    return (p)




p = {}
p['provider'] = 'g'
p['type'] = 's'
p['lat'] = 55.753739
p['lon'] = 37.619904
p['zoom'] = 14
p['steps_x'] = 9
p['steps_y'] = 13

p = initialize(p)
download_map(p)
stitch_horizontal(p)
stitch_vertical(p)

print('Done')





