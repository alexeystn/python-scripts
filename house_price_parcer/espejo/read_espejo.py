import numpy as np
from matplotlib import pyplot as plt
import cv2

# load "pik-espejo.ru" screenshot here:
filename = 'pik5feb.png'

key_colors = {    
    'red': [223, 223, 247],
    'green': [153, 235, 173],
    'white': [248, 248, 248],
    'gray': [204, 204, 204]
    }

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(np.sum(img[y,x,:]))
        
def mask_colors(img, color_name):
    m = img == key_colors[color_name]
    return np.all(m, axis=2)
    
def find_centers(img, axis):
    threshold = 20
    mask = mask_colors(img, 'red') + mask_colors(img, 'green')
    mask_1d = np.sum(mask, axis=axis) > threshold
    mask_1d_diff = np.diff(mask_1d.astype('int'))
    rising_edge = np.where(mask_1d_diff == 1)[0]
    falling_edge = np.where(mask_1d_diff == -1)[0]
    centers = ((falling_edge + rising_edge)/2).astype('int')
    return centers

img = cv2.imread(filename)
y_centers = find_centers(img, 1)
x_centers = find_centers(img, 0)

flats = {'sold': 0, 'available': 0, 'undefined': 0, 'reserved': 0, 'total': 0}

for x in x_centers:
    for y in y_centers:

        p = img[y,x,:]
        if np.all(p == key_colors['red']):
            flats['sold'] += 1
        elif np.all(p == key_colors['green']):
            flats['available'] += 1
        elif np.all(p == key_colors['white']):
            flats['undefined'] += 1
        elif np.all(p == key_colors['gray']):
            flats['reserved'] += 1
        else:
            print(x,y,'unknown color')
        flats['total'] += 1
        cv2.circle(img, (x, y), 5, (0, 0, 0), 4)


for k in flats.keys():
    print('{0:>6s}: {1}'.format(k, flats[k]))

cv2.imshow('pik', img)
cv2.setMouseCallback('pik', click)
cv2.waitKey()
cv2.destroyAllWindows()
