import cv2
import numpy as np


def pick(event, x, y, flags, param):
    _, _ = flags, param
    if event == cv2.EVENT_LBUTTONDOWN:
        print('[' + ', '.join([str(i) for i in img_part[y, x, :]]) + ']')


img = cv2.imread('map.jpg')
img_part = img[3500:4000, 1500:2000, :]
cv2.imshow('image', img_part)
cv2.setMouseCallback('image', pick)

while True:
    if cv2.waitKey(100) != -1:
        break

cv2.destroyAllWindows()
