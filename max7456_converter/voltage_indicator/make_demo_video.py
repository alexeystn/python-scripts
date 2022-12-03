import cv2
import numpy as np

filename = 'bottle'

def get_mask(img):
    mid_column = 5
    mid_row = 9
    s1 = s2 = mid_row
    while img[s1-1,mid_column] == 0:
        s1 -= 1
    while img[s2,mid_column] == 0:
        s2 += 1
    mask = []
    for i in range(s1, s2):
        s3 = s4 = mid_column
        while img[i,s3-1] == 0:
            s3 -= 1
        while img[i,s4] == 0:
            s4 += 1
        mask.append([i, s3,s4]) #  row / left / right
    return np.array(mask)


class Writer(cv2.VideoWriter):

    res = (960,720)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

    def __init__(self, filename):
        super().__init__('./video/' + filename + '.mp4', self.fourcc, 30, self.res)
        self.volt = cv2.imread('volts.png')

    def put(self, image, empty=False):
        scale = 2
        img_copy = cv2.resize(img, (12*scale, 18*scale), interpolation=cv2.INTER_NEAREST_EXACT)
        img_volt = cv2.resize(self.volt, (12*4*scale, 18*scale), interpolation=cv2.INTER_NEAREST_EXACT)
        img_full = np.zeros((self.res[1], self.res[0], 3), dtype='uint8')
        img_full[:] = img_copy[0,0]
        if not empty:
            v = self.res[1] // 2
            h = self.res[0] // 2
            for i in range(3):  # all colors
                img_full[v-scale*9:v+scale*9, h-6*scale:h+6*scale,i] = img_copy
            img_full[v-scale*9:v+scale*9, h+6*scale:h+6*scale+4*12*scale,:] = img_volt
                
        for i in range(6):
             self.write( img_full )


wr = Writer(filename)

img = cv2.imread('./image/' + filename + '.png')
img = img[:,:,0]
empty = img.copy()
empty[:] = img[0,0]

mask = get_mask(img)

for cycle in range(2):

    for i in range(len(mask)):  # Fill
        m = mask[-i-1,:]
        img[m[0],m[1]:m[2]] = 255

    for i in range(len(mask)):  # Discharge
        m = mask[i,:]
        img[m[0],m[1]:m[2]] = 0
        wr.put(img)

    for i in range(3):  # Blink
        wr.put(img)
        wr.put(img, empty=True)

    for i in range(len(mask)):  # Charge
        m = mask[-i-1,:]
        img[m[0],m[1]:m[2]] = 255
        wr.put(img)
    
wr.release()

