import cv2
import numpy as np
import random

CARD_SPACE = 10
CARD_SIZE_X = 100
CARD_SIZE_Y = 75
CARD_NUM_X = 3
CARD_NUM_Y = 2
IMAGES_NUM = CARD_NUM_X * CARD_NUM_Y // 2

combination = []
status = [] # 0 - removed, 1 - closed, 2 - open

clicked_point = 0

def generate_field():
    global combination, status 
    global CARD_SPACE, CARD_SIZE_X, CARD_SIZE_Y, CARD_NUM_X, CARD_NUM_Y

    image = np.ones((CARD_SPACE * (CARD_NUM_Y + 1) + CARD_NUM_Y * CARD_SIZE_Y,
                     CARD_SPACE * (CARD_NUM_X + 1) + CARD_NUM_X * CARD_SIZE_X, 3), np.uint8) * 255
    for x in range(CARD_NUM_X):
        for y in range(CARD_NUM_Y):
            base_x = CARD_SPACE + (CARD_SIZE_X + CARD_SPACE) * x
            base_y = CARD_SPACE + (CARD_SIZE_Y + CARD_SPACE) * y
            if status[y, x] == 0:
                continue
            if status[y, x] == 2:
                filename = './img/{0:02d}.jpg'.format(combination[y, x])
                card_image = cv2.imread(filename)
                card_image = cv2.resize(card_image, (CARD_SIZE_X, CARD_SIZE_Y), cv2.INTER_CUBIC)
            else:
                card_image = 200 # default grey color
            image[base_y:base_y+CARD_SIZE_Y, base_x:base_x+CARD_SIZE_X, :] = card_image
    return image


def click(event, x, y, flags, param):
    global clicked_point
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = [y, x]


            
step_counter = 1

opened_cards_count = 0

window_name = 'Memo'
status = np.ones((CARD_NUM_Y, CARD_NUM_X), np.uint8)
combination = np.concatenate((np.arange(IMAGES_NUM), np.arange(IMAGES_NUM)))
random.shuffle(combination)
combination = combination.reshape(CARD_NUM_Y, CARD_NUM_X)

image = generate_field()

cv2.imshow(window_name, image)
cv2.setMouseCallback(window_name, click)

while True:
    key = cv2.waitKey(1)
    if key == 27:
        break;
    if clicked_point:
        y, x = clicked_point
        if (x % (CARD_SIZE_X + CARD_SPACE) > CARD_SPACE) & (y % (CARD_SIZE_Y + CARD_SPACE) > CARD_SPACE):
            x = x // (CARD_SIZE_X + CARD_SPACE)
            y = y // (CARD_SIZE_Y + CARD_SPACE)
            if status[y, x] == 1:
                clicked_card = (y, x)
                if opened_cards_count == 0:
                    opened_cards_count = 1
                    y0, x0 = clicked_card
                    status[y0, x0] = 2
                    image = generate_field()
                    cv2.imshow(window_name, image)
                elif opened_cards_count == 1:
                    opened_cards_count = 2
                    y1, x1 = clicked_card
                    status[y1, x1] = 2
                    image = generate_field()
                    cv2.imshow(window_name, image)
                    cv2.waitKey(1000)
                    step_counter += 1
                    if combination[y0, x0] == combination[y1, x1]:
                        status[y0, x0] = 0
                        status[y1, x1] = 0
                        if not status.any():
                            break
                    else:
                        status[y0, x0] = 1
                        status[y1, x1] = 1
                    opened_cards_count = 0
                    image = generate_field()
                    cv2.imshow(window_name, image)
        clicked_point = 0

print('Solved in {0} steps'.format(step_counter))
cv2.destroyAllWindows()


