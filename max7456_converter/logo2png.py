# Add LOGO image (288 × 72)
# to FONT image (256 characters)

import cv2
import numpy as np

img_in_filename = 'bold_hr.png'
img_out_filename = 'bold_hr_logo.png'

img_font = cv2.imread(img_in_filename)
img_logo = cv2.imread('logo.bmp')

w = 12
h = 18
dn = 10*16 # logo starts from 10th row

for i in range(256-dn):
    xL = (i % 24) * w
    yL = (i // 24) * h
    char = img_logo[yL:yL+h, xL:xL+w]

    mask = (char[:,:,0] == 0) * (char[:,:,1] == 255) # green
    char[mask] = 127

    xF = ((i+dn) % 16) * (w + 1)
    yF = ((i+dn) // 16) * (h + 1)
    img_font[yF:yF+h, xF:xF+w] = char

cv2.imwrite(img_out_filename, img_font)

#cv2.imshow('Result', img_font)
