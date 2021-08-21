import numpy as np
import cv2 as cv


def show(img, delay=0):

    h = img.shape[0] // 2
    w = img.shape[1] // 2
    img_small = cv.resize(img, (w, h))
    cv.imshow('Output', img_small)
    if delay == 0:
        cv.waitKey()
    else:
        cv.waitKey(int(delay*1000))


def resize(img):

    h = img.shape[0] * 4 // 3
    w = img.shape[1]   
    return cv.resize(img, (w, h))


def gen_pattern_grid(size=(4,11)):

    pattern_grid = []
    for i in range(size[1]):
        for j in range(size[0]):
            pattern_grid.append([(2*j)+i%2,i,0])
    return np.asarray(pattern_grid, dtype='f4')

