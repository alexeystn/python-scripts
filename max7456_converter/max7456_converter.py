import cv2
import numpy as np


class Font:

    colors = {'01': 127, '10': 255, '00': 0}

    def __init__(self):
        self.symbols = np.zeros((256, 18, 12), dtype='uint8')
        self.image = np.zeros(((18 + 1) * 16, (12 + 1) * 16, 3), dtype='uint8')
        self.image[:, :, 1] = 255  # red background

    def load_from_mcm(self, filename):
        with open(filename, 'r') as f:
            f.readline()
            for char in range(256):
                for py in range(18):
                    for px in range(3):
                        line = f.readline()
                        for ix in range(4):
                            pixel = line[ix*2:ix*2+2]
                            self.symbols[char, py, px*4+ix] = self.colors[pixel]
                for i in range(10):  # 64 - 18*12/4
                    f.readline()
        self.update_image()

    def update_image(self):
        for cy in range(16):
            for cx in range(16):
                char = self.symbols[cy*16+cx]
                x0 = cx*(12+1)
                x1 = (cx+1)*(12+1)-1
                y0 = cy*(18+1)
                y1 = (cy+1)*(18+1)-1
                for i in range(3):
                    self.image[y0:y1, x0:x1, i] = char

    def load_from_png(self, filename):
        input_image = cv2.imread(filename)
        for ch in range(256):
            cx = ch % 16
            cy = ch // 16
            x0 = cx * (12 + 1)
            x1 = (cx + 1) * (12 + 1) - 1
            y0 = cy * (18 + 1)
            y1 = (cy + 1) * (18 + 1) - 1
            char = input_image[y0:y1, x0:x1, 0]
            self.symbols[ch] = char
        self.update_image()

    def save_to_mcm(self, filename):
        with open(filename, 'w') as f:
            f.write('MAX7456')
            for cn in range(256):
                for y in range(18):
                    for x1 in range(3):
                        line = self.symbols[cn, y, x1*4:(x1+1)*4]
                        s = ''
                        for px in line:
                            if px == 255:
                                s += '10'
                            elif px == 0:
                                s += '00'
                            else:
                                s += '01'
                        f.write('\n' + s)
                for t in range(10):
                    f.write('\n' + '01010101')

    def save_to_png(self, filename):
        cv2.imwrite(self.image, filename)

    def add_logo(self, filename):
        input_logo = cv2.imread(filename)
        for yl in range(4):
            for xl in range(24):
                char_logo = input_logo[yl*18:(yl+1)*18, xl*12:(xl+1)*12, :]
                char_logo = np.mean(char_logo, axis=2)
                char_logo[(char_logo > 0) & (char_logo < 255)] = 127
                n = 10 * 16 + yl * 24 + xl   # logo starts from 10th row
                self.symbols[n] = char_logo
        self.update_image()

    def show(self):
        self.update_image()
        cv2.imshow('Font', font.image)
        cv2.waitKey(0)


font = Font()

font.load_from_png('source/default_ovp.png')
font.add_logo('source/logo.bmp')
font.save_to_mcm('default_ovp.mcm')
font.show()
