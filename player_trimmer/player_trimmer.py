import cv2
import time
import os
import sys
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

input_filename = filedialog.askopenfilename()
path_split = os.path.split(input_filename)

output_filename = path_split[-1]
if not output_filename:
    sys.exit(0)

print(output_filename)
output_filename = output_filename.split(sep='.')[0]
output_filename += '_trim.mp4'

codec = "h264" # "mp4v" / "h264"

vcap = cv2.VideoCapture(input_filename)

rewind = -1
is_playing = True
position = 0

width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(round(vcap.get(cv2.CAP_PROP_FPS)))
frame_count = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))

width_out = 640


left_cursor = -1
right_cursor = frame_count
is_playing_selection = False

mouse_hold = False
was_playing_before_hold = True


def save_selection():
    #output_filename = 'trim.mp4'
    video_writer = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc(*codec),
                               fps, (width_out, height))
    video_writer.set(cv2.VIDEOWRITER_PROP_QUALITY, 100)
    vcap.set(cv2.CAP_PROP_POS_FRAMES, left_cursor-1)
    result, image = vcap.read()

    length = right_cursor - left_cursor - 1
    for fr in range(length):
        res, img = vcap.read()
        img = cv2.resize(img, (width_out, height))
        video_writer.write(img)
        if fr % 10 == 0 or fr == length - 1:
            print('{0:.2f}%'.format((fr/(length-1))*100))
    video_writer.release()


def print_selection():
    if left_cursor != -1 and right_cursor != frame_count:
        selection_length = (right_cursor - left_cursor)/fps
        print('Selected {0:.2f} seconds'.format(selection_length))


def print_text(image, text, x, y):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    cv2.putText(image, str(text), (x,y), font, 0.7, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(image, str(text), (x,y), font, 0.7, (255,255,255), 2, cv2.LINE_AA)


def draw_bar(image, pos):
    print_text(image, str(pos), 10, height//4)
    if pos == left_cursor:
        print_text(image, 'Start', width//2-60, height//4)
    if pos == right_cursor:
        print_text(image, 'Stop', width//2-60, height//4)
    bar_h = 10
    cv2.rectangle(image, (0, height // 2 - bar_h), (int(width / 2) - 1, height//2-1),
                  (0,0,0), -1)
    cv2.rectangle(image, (1, height // 2 - bar_h + 1), (int(width * pos / 2 / frame_count), height//2-2),
                  (255,255,255), -1)

    y2 = height // 2 - bar_h
    y1 = height // 2 - 1
    x = int(width * left_cursor / 2 / frame_count)
    if left_cursor != -1:
        cv2.rectangle(image, (x-1, y1), (x+2, y2), (0,0,255), -1)
    x = int(width * right_cursor / 2 / frame_count)
    if right_cursor != frame_count:
        cv2.rectangle(image, (x-1, y1), (x+2, y2), (0,192,0), -1)
    

def on_mouse(event, x, y, a, b):
    global rewind, mouse_hold, is_playing, was_playing_before_hold, frame_count
    #print(event)
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_hold = True
        was_playing_before_hold = is_playing
        is_playing = False
    if mouse_hold:
        rewind = int(x * frame_count * 2 / width)
        if rewind < 0:
            rewind = 0
        if rewind > frame_count:
            rewind = frame_count - 1
        is_playing = False
    if event == cv2.EVENT_LBUTTONUP:
        mouse_hold = False
        if was_playing_before_hold: 
            is_playing = True
        

cv2.namedWindow(input_filename)
cv2.setMouseCallback(input_filename, on_mouse)

next_time = 0

while True:
    
    while time.time() < next_time:
        continue
    next_time = time.time() + 1/fps
    if rewind != -1:
        position = rewind
        rewind = -1

    
    vcap.set(cv2.CAP_PROP_POS_FRAMES, position)
    result, image = vcap.read()

    image = cv2.resize(image, (width//2, height//2))
    draw_bar(image, position)
    cv2.imshow(input_filename, image)
    
    if position == right_cursor and is_playing_selection:
        is_playing_selection = False
        is_playing = False

    if position == frame_count - 1:
        is_playing = False
        
    if is_playing:
        position += 1
    
    k = cv2.waitKeyEx(1)
    if k != -1:
        is_playing_selection = False
    if k == 27: # Esc
        break
    if k == 32: # Space
        is_playing = not is_playing
    if k == 2424832 or k == 44 or k == 63234: # left <
        is_playing = False
        if position > 0:
            position -= 1
    if k == 2555904 or k == 46 or k == 63235: # right >
        is_playing = False
        if position < frame_count:
            position += 1
    if k == 49: # '1'
        left_cursor = position
        print('Set Start to', position)
        print_selection()
    if k == 50: # '2'
        right_cursor = position
        print('Set Stop to', position)
        print_selection()
    if k == 13: # Enter
        is_playing_selection = True
        is_playing = True
        position = left_cursor
    if k == 10 or k == 9: # Ctrl+Enter / Tab
        is_playing_selection = False
        is_playing = False
        save_selection();
    if k != -1:
        print(k)
    
    if cv2.getWindowProperty(input_filename,0) < 0:
       break

cv2.destroyAllWindows()
