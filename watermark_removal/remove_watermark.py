import cv2
import json
import numpy as np

img = cv2.imread('map.jpg')
# img = img[2000:2500, 3000:3500, :]
# cv2.imshow('image', img)

LEVEL_THRESHOLD = 5
DILATE_SIZE = 3
MEDIAN_BLUR_SIZE = 5
GAUSSIAN_BLUR_SIZE = 3
POLYNOM = [1.17451443, 3.17912306]

with open('colors.txt', 'r') as f:
    colors = json.loads(f.read())

mask = np.zeros(img.shape[:-1], dtype='bool')
img_i16 = img.astype('int16')

for color in colors.keys():
    color_in = np.array(colors[color]).astype('int16')
    mask = mask + ((np.abs(img_i16 - color_in)).sum(axis=2) < LEVEL_THRESHOLD)
    print(color)

mask = (mask * 255).astype('uint8')
# cv2.imwrite('mask_1.png', mask)
mask = cv2.medianBlur(mask, MEDIAN_BLUR_SIZE)
# cv2.imwrite('mask_2.png', mask)
mask = cv2.dilate(mask, np.ones((DILATE_SIZE, DILATE_SIZE)))
# cv2.imwrite('mask_3.png', mask)
mask = cv2.blur(mask, (GAUSSIAN_BLUR_SIZE, GAUSSIAN_BLUR_SIZE), 0)
# cv2.imwrite('mask_4.png', mask)

img_new = np.zeros(img.shape)

for i in range(3):
    img_new[:, :, i] = img[:, :, i] * (1 - mask/255.0) + \
        (img[:, :, i] * POLYNOM[0] + POLYNOM[1]) * (mask/255.0)

cv2.imwrite('output.jpg', img_new)
