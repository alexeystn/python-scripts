import cv2
import numpy as np
import time
import random
import colorsys

pad = 10
size_x = 120
size_y = 80

num_x = 4
num_y = 6

num_img = num_x * num_y // 2

image = 0
combination = 0
card_status = 0

card_clicked = 0


def generate_field(card_status, combination):
    global num_x, num_y, size_x, size_y, pad
    image = np.ones((pad * (num_y+1) + num_y * size_y, pad * (num_x+1) + num_x * size_x, 3), np.uint8) * 255
    for x in range(num_x):
        for y in range(num_y):
            base_x = pad + (size_x + pad) * x
            base_y = pad + (size_y + pad) * y
            if card_status[y, x] == 0:
                continue
            if card_status[y, x] == 2:
                filename = './img/{0:02d}.jpg'.format(combination[y, x])
                im = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                im = cv2.resize(im, (size_x, size_y), cv2.INTER_CUBIC)
            else:
                im = 200
            image[base_y:base_y+size_y, base_x:base_x+size_x, :] = im
    return image


def click(event, x, y, flags, param):
    global size_x, size_y, pad
    global card_status
    global card_clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        x_int = x // (size_x + pad)
        x_frac = x % (size_x + pad)
        y_int = y // (size_y + pad)
        y_frac = y % (size_y + pad)
        if (x_frac > pad) & (y_frac > pad):
            if card_status[y_int, x_int] == 1:
                card_clicked = (y_int, x_int)
    return
            
counter = 1

opened_cards_number = 0

window_name = 'Memo'
card_status = np.ones((num_y, num_x), np.uint8)
combination = np.concatenate((np.arange(num_img), np.arange(num_img)))
random.shuffle(combination)
combination = combination.reshape(num_y, num_x)

image = generate_field(card_status, combination)

cv2.imshow(window_name, image)
cv2.setMouseCallback(window_name, click)

while True:
    key = cv2.waitKey(1)
    if key == 27:
        break;
    if card_clicked: 
        if opened_cards_number == 0:
            opened_cards_number = 1
            x0 = card_clicked[1]
            y0 = card_clicked[0]
            card_status[y0, x0] = 2
            image = generate_field(card_status, combination)
            cv2.imshow(window_name, image)
        elif opened_cards_number == 1:
            opened_cards_number = 2
            x1 = card_clicked[1]
            y1 = card_clicked[0]
            card_status[y1, x1] = 2
            image = generate_field(card_status, combination)
            cv2.imshow(window_name, image)
            cv2.waitKey(1000)
            counter += 1
            if combination[y0, x0] == combination[y1, x1]:
                card_status[y0, x0] = 0
                card_status[y1, x1] = 0
                if not card_status.any():
                    print('Solved in {0} steps'.format(counter))
                    break
            else:
                card_status[y0, x0] = 1
                card_status[y1, x1] = 1                
            image = generate_field(card_status, combination)
            cv2.imshow(window_name, image)
            opened_cards_number = 0
        print(card_clicked)
        card_clicked = 0

cv2.destroyAllWindows()

