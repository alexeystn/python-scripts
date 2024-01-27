import cv2
import numpy as np


class Box:

    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    gamma = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    notes_b = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
    height = 120
    width = 200
    radius = 50
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = 2.4
    font_thickness = 6
    line_thickness = 4
    point_size = 10
    margin = 150

    bg_color = [0, 50, 100]
    bg_color_minor = [255, 255, 255]
    bg_color_major = [255, 255, 255]
    bg_color_normal = [255, 255, 255]
    bg_color_unused = [0, 0, 0]
    txt_color_minor = [0, 0, 0]
    txt_color_major = [0, 0, 0]
    txt_color_normal = [0, 0, 0]
    txt_color_unused = [150, 150, 150]
    string_color = [180, 180, 180]
    fret_color = [50, 160, 200]
    point_color = [200, 200, 200]

    default_box_width = 8
    penta_box_width = 15

    def generate_boxes(self, start, pentatonic=False):
        result = []
        notes = self.notes * 4
        pos = notes.index(self.gamma[start])
        if pentatonic:
            box_width = self.penta_box_width
        else:
            box_width = self.default_box_width
        for i in range(6):
            start %= 7
            stop = (start + 2) % 7
            part = notes[pos:pos+box_width]
            start_index = part.index(self.gamma[start])
            stop_index = part.index(self.gamma[stop])
            if pentatonic:
                result.append((part, (0, box_width-1)))
            else:
                result.append((part, (start_index, stop_index)))
            pos += 5
            if i == 3:
                pos -= 1
            start += 3
        return result

    def draw_box(self, box, pentatonic=False, show=False):

        if pentatonic:
            box_width = self.penta_box_width
        else:
            box_width = self.default_box_width

        img = np.zeros((self.height*7, self.width*box_width, 3), dtype='uint8')
        img[:, :] = self.bg_color

        last_string = box[0][0]
        for i in range(box_width+1):
            cv2.line(img, (self.width//2 + self.width*i, self.height//2),
                     (self.width // 2 + self.width * i, self.height // 2 + self.height * 6),
                     self.fret_color, self.line_thickness*2)
            y = int(6.75 * self.height)
            x = (i + 1) * self.width
            if i < len(last_string) - 1:
                if last_string[i] in ['G', 'A', 'B', 'C#']:
                    cv2.circle(img, (x, y), self.point_size, self.point_color, -1)
                if last_string[i] == 'E':
                    cv2.circle(img, (x - self.point_size * 2, y),
                               self.point_size, self.point_color, -1)
                    cv2.circle(img, (x + self.point_size * 2, y),
                               self.point_size, self.point_color, -1)
        
        for i in range(6):
            y = (6 - i) * self.height
            cv2.line(img, (0, y), (self.width*box_width, y), self.string_color,
                     self.line_thickness)

            start, stop = box[i][1]
            for j in range(box_width-1):
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
                    highlight = False
                    if pentatonic and txt in 'ACDEG':
                        highlight = True
                    if not pentatonic and not txt.endswith('#'):
                        highlight = True
                    if highlight:
                        txt_color = self.txt_color_normal
                        bg_color = self.bg_color_normal
                    if txt == 'A':
                        bg_color = self.bg_color_minor
                        txt_color = self.txt_color_minor
                    elif txt == 'C':
                        bg_color = self.bg_color_major
                        txt_color = self.txt_color_major

                cv2.circle(img, (x, y), self.radius, bg_color, -1)
                centers = cv2.getTextSize(txt, self.font, scale, font_thickness)[0]

                cv2.putText(img, txt, (x - centers[0]//2, y + centers[1]//2 - int(self.scale*2)),
                            self.font, scale, txt_color, font_thickness)

                cv2.circle(img, (x, y), self.radius, [0, 0, 0], self.line_thickness)

        if show:
            cv2.imshow('img', img)
            cv2.waitKey()
            cv2.destroyAllWindows()

        return img

    def draw_all_boxes(self):

        h = self.height * 7
        w = self.width * self.default_box_width
        m = self.margin

        img = np.ones((5*m+4*h, 3*m+w*2, 3), dtype='uint8')

        for i in range(7):
            bx = self.generate_boxes(i)
            img_bx = self.draw_box(bx)
            x = m + (m + w) * (i % 2)
            y = m + (m + h) * (i // 2)
            img[y:y+h, x:x+w, :] = img_bx

        cv2.imwrite('boxes.png', img)
        return

    def draw_pentatonics(self):

        h = self.height * 7
        w = self.width * self.penta_box_width
        m = self.margin

        img = np.ones((2*m+h, 2*m+w, 3), dtype='uint8') * 255

        bx = self.generate_boxes(4, pentatonic=True)
        img_bx = self.draw_box(bx, pentatonic=True)
        img[m:m+h, m:m+w, :] = img_bx
        
        cv2.imwrite('penta.png', img)
        return
        
    def draw_circle_of_fifths(self):

        margin = 80
        radius_internal = 250
        radius_external = 620
        radius_middle = 410
        center = radius_external + margin
        color = [0, 0, 0]
        w = radius_external*2 + margin*2
        img = np.ones((w, w, 3), dtype='uint8') * 255
        font = cv2.FONT_HERSHEY_DUPLEX
        scale = 4.0
        font_thickness = 6
        minor_scale = 2
        line_thickness = font_thickness
        radius_major = int((radius_external + radius_middle) / 2)
        radius_minor = int((radius_internal + radius_middle) / 2)
        cv2.circle(img, (center, center), radius_external, color, line_thickness)
        cv2.circle(img, (center, center), radius_middle, color, line_thickness)
        cv2.circle(img, (center, center), radius_internal, color, line_thickness)

        for i in range(12):
            t = np.pi * ( (0.5 + i) / 6)
            sin = np.sin(t)
            cos = np.cos(t)
            p0 = (center + int(radius_internal * sin),
                  center + int(radius_internal * cos))
            p1 = (center + int(radius_external * sin),
                  center + int(radius_external * cos))            
            cv2.line(img, p0, p1, color, line_thickness)
        
        for i in range(12):
            sin = np.sin(np.pi * (i / 6))
            cos = np.cos(np.pi * (i / 6))
            p = (center + int(radius_major * cos),
                  center + int(radius_major * sin))
            txt = self.notes_b[(i*7) % 12]
            centers = cv2.getTextSize(txt, self.font, scale, font_thickness)[0]    
            cv2.putText(img, txt, (p[0] - centers[0]//2, p[1] + centers[1]//2),
                        self.font, scale, color, font_thickness)
            p = (center + int(radius_minor * cos),
                  center + int(radius_minor * sin))
            if i < 3:
                txt = self.notes[(i*7 - 3) % 12] + 'm'
            else:
                txt = self.notes_b[(i*7 - 3) % 12] + 'm'
            centers = cv2.getTextSize(txt, self.font, int(scale/minor_scale),
                                      int(font_thickness / minor_scale))[0]
            cv2.putText(img, txt, (p[0] - centers[0]//2, p[1] + centers[1]//2),
                        self.font, scale/minor_scale, color, int(font_thickness / minor_scale))
                        
        cv2.imwrite('circle.png', img)


b = Box()
b.draw_pentatonics()
b.draw_all_boxes()
b.draw_circle_of_fifths()
