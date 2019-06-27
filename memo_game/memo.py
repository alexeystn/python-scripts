import cv2
import numpy as np
import random

pad = 10
size_x = 100
size_y = 75

num_x = 5
num_y = 10

num_img = num_x * num_y // 2

image = 0
combination = 0
card_status = 0

card_clicked = 0

clicked_point = 0

clicked_point = 0

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
                print(filename)
                im = cv2.imread(filename)
                im = cv2.resize(im, (size_x, size_y), cv2.INTER_CUBIC)
            else:
                im = 200
            image[base_y:base_y+size_y, base_x:base_x+size_x, :] = im
    return image


def click(event, x, y, flags, param):
    global clicked_point
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = y, x


            
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
    if clicked_point:
        y, x = clicked_point
        
        if (x % (size_x + pad) > pad) & (y % (size_y + pad) > pad):
            x = x // (size_x + pad)
            y = y // (size_y + pad)
            print(x, y)
            if card_status[y, x] == 1:
                card_clicked = (y, x)
                
                if opened_cards_number == 0:
                    opened_cards_number = 1
                    y0, x0 = card_clicked
                    card_status[y0, x0] = 2
                    image = generate_field(card_status, combination)
                    cv2.imshow(window_name, image)
                elif opened_cards_number == 1:
                    opened_cards_number = 2
                    y1, x1 = card_clicked
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
        clicked_point = 0

cv2.destroyAllWindows()

