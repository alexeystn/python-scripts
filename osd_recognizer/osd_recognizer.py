from PIL import Image, ImageDraw
import numpy as np

class OSD_Recognizer:

    ch_w = 12
    ch_h = 18
    ch_hor = 28
    ch_vert = 15
    threshold = 20
    img_height = ch_h*ch_vert
    img_width = ch_w*ch_hor
    box = ( 7, 29,  640, 479 )
    font = np.zeros((10, ch_w, ch_h))
    font_coef = np.zeros(10)
    img = Image
    img_grid = Image
    debug = 0

    def display_font_char(self, num):
        for y in range(self.ch_h):
            s = ''
            for x in range(self.ch_w):
                p = self.font[num, x, y]
                if p > 0:
                    s += 'x'
                elif p < 0:
                    s += '-'
                else:
                    s += ' '
            print(s)

    def load_image(self, photofile_name):
        self.img = Image.open(photofile_name);
        self.img = self.img.crop(self.box)
        self.img = self.img.resize((self.img_width, self.img_height), Image.ANTIALIAS)

    def draw_grid(self, gridfile_name):
        img_grid = self.img
        drw = ImageDraw.Draw(img_grid)
        for x in range(0, self.img_width, self.ch_w):
            drw.line( (x, 0, x, self.img_height), fill='black')
            drw.line( (x-1, 0, x-1, self.img_height), fill='black')

        for y in range(0, self.img_height, self.ch_h):
            drw.line( (0, y, self.img_width, y), fill='black')
            drw.line( (0, y-1, self.img_width, y-1), fill='black')
        self.img.save(gridfile_name)
        self.img_grid = img_grid

    def load_font(self, fontfile_name):
        fnt_img = Image.open(fontfile_name);
        for i in range(10):
            chr_img = fnt_img.crop((i*self.ch_w,0,(i+1)*self.ch_w, self.ch_h))
            for y in range(self.ch_h):
                for x in range(self.ch_w):
                    p = chr_img.getpixel((x, y))
                    if p < 10:
                        self.font[i, x, y] = -1
                        self.font_coef[i] += 1
                    elif p > 240:
                        self.font[i, x, y] = 1
                        self.font_coef[i] += 1
                    else:
                        self.font[i, x, y] = 0

    def char_correlation(self, im, num):
        c = 0
        for x in range(self.ch_w):
            for y in range(self.ch_h):
                px = im.getpixel((x,y))
                p = (px[0]+px[1]+px[2])/3 - 128
                c += p * self.font[num, x, y]
        c /= self.font_coef[num]
        return c

    def recognize_char(self, c_x, c_y):
        box = (c_x*self.ch_w, c_y*self.ch_h, (c_x+1)*self.ch_w, (c_y+1)*self.ch_h)
        im_char = self.img.crop(box)
        corr = [];
        for i in range(10):
            c = self.char_correlation(im_char, i)
            corr.append(c)
        max_corr = max(corr)
        if self.debug:
            print(corr)
        for i, j in enumerate(corr):
            if j == max_corr:
                max_num = i
        if max_corr > self.threshold:        
            return max_num
        else:
            return ' '

    def recognize_line(self, start, length):
        s = ''
        for x in range(length):
            c = self.recognize_char(start[0]+x, start[1])
            s += str(c)
        return s

        
