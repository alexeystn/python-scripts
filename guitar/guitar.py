import cv2
import numpy as np


class Box:

    notes = 'ABCDEFG'
    height = 120
    width = 200
    radius = 50
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = 2.4
    font_thickness = 6
    line_thickness = 6  # thickness
    margin = 150

    def print_box(self, lines):

        for i in range(6):
            print_line = ['-'] * 7
            line = lines[6-i-1]
            for nt in line:
                print_line[line[nt]] = nt
            print('|-' + '-|-'.join(print_line) + '-|')
        print()

    def get_lines(self, start):

        pos = self.notes.index(start)
        fret_pos = 0

        lines = []

        for i in range(6):
            lines.append({})
            for j in range(3):
                nt = self.notes[pos % 7]
                lines[i][nt] = fret_pos
                pos += 1
                fret_pos += 1 if nt in 'BE' else 2
            fret_pos -= 4 if i == 3 else 5

        return lines

    def draw_all_boxes(self):

        h = self.height * 7
        w = self.width * 8
        m = self.margin

        img = np.ones((5*m+4*h, 3*m+w*2, 3), dtype='uint8')

        for i in range(7):
            img_box = self.draw_box(self.get_lines(self.notes[i]))
            x = m + (m + w) * (i % 2)
            y = m + (m + h) * (i // 2)
            img[y:y+h, x:x+w, :] = img_box

        cv2.imwrite('img.png', img)
        return

    def draw_box(self, lines, show=False):

        color_notes = [0, 0, 0]
        color_white = [255, 255, 255]
        color_minor = [255, 30, 30]
        color_major = [0, 0, 230]

        color_background = 255

        img = np.ones((self.height*7, self.width*8, 3), dtype='uint8') * color_background

        for i, line in enumerate(lines):
            y = (6 - i) * self.height
            cv2.line(img, (0, y), (self.width*8, y), [0, 0, 0], self.line_thickness)
            for j in range(7):
                x = (j + 1) * self.width
                cv2.circle(img, (x, y), self.radius, [0, 0, 0], -1, self.line_thickness)

            random_note = list(line.keys())[0]
            note_number = self.notes.find(random_note)
            note_pos = line[random_note]
            offset = note_number - note_pos
            for j in range(7):
                txt = self.notes[(j + offset) % 7]
                x = (j + 1) * self.width
                cv2.putText(img, txt, (x, y),
                            self.font, self.scale/2, [255, 255, 255], self.font_thickness)

            for k in line:
                color = color_notes
                if k == 'A':
                    color = color_minor
                if k == 'C':
                    color = color_major
                x = (line[k] + 1) * self.width
                cv2.circle(img, (x, y), self.radius, color, -1)

                centers = cv2.getTextSize(k, self.font, self.scale, self.font_thickness)[0]
                cv2.putText(img, k, (x - centers[0]//2, y + centers[1]//2 - int(self.scale*2)),
                            self.font, self.scale, [255, 255, 255], self.font_thickness)

            for j in range(7):
                x = (j + 1) * self.width
                cv2.circle(img, (x, y), self.radius, [0, 0, 0], self.line_thickness)

        for i in range(8):
            cv2.line(img, (self.width//2 + self.width*i, self.height//2),
                     (self.width // 2 + self.width * i, self.height // 2 + self.height * 6),
                     [0, 0, 0], self.line_thickness)

        if show:
            cv2.imshow('img', img)
            cv2.waitKey()

        return img


b = Box()
b.draw_all_boxes()
