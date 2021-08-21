import requests
import numpy as np
import cv2
import time

ft = '0cceae18c4d6cca9c76193b31840363c61e11aadd3a1f6d66fc29dab97600740ef37a17e3dadf23df49f639c2'

path = './images/'

left = 15
top = 56
width = 24
height = 18
a = 200

full_map = np.zeros((height*a, width*a, 3), np.uint8)

for y in range(height):
    for x in range(width):
        ix = x + left - width//2
        iy = y + top - height//2
        url = 'http://map1.etomesto.ru/genshtab/o37-v/{0}/{1:d}_{2:d}.jpg'.format(ft[ix], ix, iy)
        response = requests.get(url)
        filename = path + url.split(sep='/')[-1]
        with open(filename, 'wb') as f:
            f.write(response.content)
        img = cv2.imread(filename)
        px = x * a
        py = y * a
        full_map[py:py+a, px:px+a, :] = img
        print('{0}/{1}'.format(y*width+x+1, height*width))
        time.sleep(0.5)

cv2.imwrite('map.png', full_map)
