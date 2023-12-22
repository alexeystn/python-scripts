import cv2
import numpy as np


class Box:

    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    gamma = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    height = 120
    width = 200
    radius = 50
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = 2.4
    font_thickness = 6
    line_thickness = 4
    margin = 150

    bg_color_minor = [255, 30, 30]
    bg_color_major = [0, 0, 230]
    bg_color_normal = [100, 100, 100]
    bg_color_unused = [250, 250, 250]
    txt_color_normal = [255, 255, 255]
    txt_color_unused = [150, 150, 150]

    def generate_boxes(self, start):
        result = []
        notes = self.notes * 4
        pos = notes.index(self.gamma[start])
        for i in range(6):
            start %= 7
            stop = (start + 2) % 7
            part = notes[pos:pos+7]
            start_index = part.index(self.gamma[start])
            stop_index = part.index(self.gamma[stop])
            result.append((part, (start_index, stop_index)))
            pos += 5
            if i == 3:
                pos -= 1
            start += 3
        return result

    def draw_box(self, box, show=False):

        img = np.ones((self.height*7, self.width*8, 3), dtype='uint8') * 255

        for i in range(6):
            y = (6 - i) * self.height
            cv2.line(img, (0, y), (self.width*8, y), [0, 0, 0], self.line_thickness)

            start, stop = box[i][1]
            for j in range(7):
                x = (j + 1) * self.width
                txt = box[i][0][j]
                scale = self.scale
                font_thickness = self.font_thickness
                if txt.endswith('#'):
                    scale /= 2
                    font_thickness //= 2
                txt_color = self.txt_color_unused
                bg_color = self.bg_color_unused
                if start <= j <= stop:
                    if not txt.endswith('#'):
                        txt_color = self.txt_color_normal
                        bg_color = self.bg_color_normal
                    if txt == 'A':
                        bg_color = self.bg_color_minor
                    elif txt == 'C':
                        bg_color = self.bg_color_major

                cv2.circle(img, (x, y), self.radius, bg_color, -1)
                centers = cv2.getTextSize(txt, self.font, scale, font_thickness)[0]

                cv2.putText(img, txt, (x - centers[0]//2, y + centers[1]//2 - int(self.scale*2)),
                            self.font, scale, txt_color, font_thickness)

                cv2.circle(img, (x, y), self.radius, [0, 0, 0], self.line_thickness)

        for i in range(8):
            cv2.line(img, (self.width//2 + self.width*i, self.height//2),
                     (self.width // 2 + self.width * i, self.height // 2 + self.height * 6),
                     [0, 0, 0], self.line_thickness)

        if show:
            cv2.imshow('img', img)
            cv2.waitKey()
            cv2.destroyAllWindows()

        return img

    def draw_all_boxes(self):

        h = self.height * 7
        w = self.width * 8
        m = self.margin

        img = np.ones((5*m+4*h, 3*m+w*2, 3), dtype='uint8')

        for i in range(7):
            bx = self.generate_boxes(i)
            img_bx = self.draw_box(bx)
            x = m + (m + w) * (i % 2)
            y = m + (m + h) * (i // 2)
            img[y:y+h, x:x+w, :] = img_bx

        cv2.imwrite('img.png', img)
        return


b = Box()
b.draw_all_boxes()
