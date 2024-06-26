import cv2
import time
import os
import sys
import wave
import tkinter as tk
import numpy as np
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

input_filename = filedialog.askopenfilename()
path_split = os.path.split(input_filename)

output_filename = path_split[-1]
if not output_filename:
    sys.exit(0)

def get_available_filename(filename):
    filename = filename.split(sep='.')[0] + '_trim'
    res = filename + '.mp4'
    cnt = 1
    while os.path.exists(res):
        res = filename + '_{0}.mp4'.format(cnt)
        cnt += 1
    return res


codec = "h264" # "mp4v" / "h264"
scale = 2 # 1 or 2

vcap = cv2.VideoCapture(input_filename)

rewind = -1
is_playing = True
position = 0

width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(round(vcap.get(cv2.CAP_PROP_FPS)))
frame_count = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))

width_out = 1280#640
height_out = 720#480

left_cursor = -1
right_cursor = frame_count
bookmarks = []
is_playing_selection = False

mouse_hold = False
was_playing_before_hold = True


def add_mark(marks, new_mark):
    if new_mark in marks:
        marks.remove(new_mark)
        new_marks = marks
    else:
        min_dist = 3 * fps # minimal distance
        new_marks = [m for m in marks if (np.abs(m - new_mark) > min_dist)]
        new_marks.append(new_mark)
    new_marks.sort()
    if len(new_marks) > 1:
        lap_times = np.diff(np.array(new_marks,dtype='float'))
        lap_times = lap_times / fps * 1.004 # Calibration coefficient
        print('Laps: ', end='')
        print(', '.join(['{0:.2f}'.format(lap) for lap in lap_times]))

    return new_marks


def compress_video(filename, wavefile, compress=True):

    spl = os.path.splitext(filename)
    new_filename = spl[0] + '_enc'
    if compress:
        new_filename += '_comp'
    new_filename += '.mp4'
    
    ffmpeg_params = ['./ffmpeg',
                     '-i', filename,
                     '-i', wavefile,
                     new_filename]
    bitrate = 4000
    if compress:
        ffmpeg_params.insert(5, '-c:v libx264')
        ffmpeg_params.insert(6, '-b:v {0}k'.format(bitrate))
        #ffmpeg_params.insert(7, '-vf "scale=640:480, setdar=4/3"')
    else:
        ffmpeg_params.insert(5, '-c:v copy')

    cmd = ' '.join(ffmpeg_params)
    #print(cmd)
    print('Encoding with \'ffmpeg\'...')  
    os.system(cmd)


def reencode_video(filename):
    wavefile = 'temp.wav'
    w = wave.open(wavefile, mode='wb')
    w.setframerate(22050)
    w.setsampwidth(2)
    w.setnchannels(1)
    w.writeframes(np.zeros((1000,2), dtype='int16'))
    w.close()

    compress_video(filename, wavefile, True)
    compress_video(filename, wavefile, False)
 
    os.remove(wavefile)
    os.remove(filename)
    print('Done')

def save_selection():
    new_filename = get_available_filename(output_filename)
    video_writer = cv2.VideoWriter(new_filename,
                                    cv2.VideoWriter_fourcc(*codec),
                                    fps, (width_out, height_out))
    vcap.set(cv2.CAP_PROP_POS_FRAMES, left_cursor-1)
    result, image = vcap.read()
    length = right_cursor - left_cursor - 1
    for fr in range(length):
        res, img = vcap.read()
        img = cv2.resize(img, (width_out, height_out))
        video_writer.write(img)
        if fr % 50 == 0 or fr == length - 1:
            print('{0:.1f}%'.format((fr/(length-1))*100))
    video_writer.release()
    reencode_video(new_filename)


def print_selection():
    if left_cursor != -1 and right_cursor != frame_count:
        selection_length = (right_cursor - left_cursor)/fps
        print('Selected {0:.2f} seconds'.format(selection_length))


def print_text(image, text, x, y):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    cv2.putText(image, str(text), (x,y), font, 0.7, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(image, str(text), (x,y), font, 0.7, (255,255,255), 2, cv2.LINE_AA)

bar_h = 15

def draw_bar(image, pos):
    #print_text(image, str(pos), 10, height//(scale*2))
    if pos == left_cursor:
        print_text(image, 'Start', width//scale-60, height//(scale*2))
    if pos == right_cursor:
        print_text(image, 'Stop', width//scale-60, height//(scale*2))

    cv2.rectangle(image, (1, height // scale + 1), (int(width * pos / scale / frame_count), height//scale+bar_h-2),
                  (255,255,255), -1)

    y2 = height // scale + 2
    y1 = height // scale - 3 + bar_h
    y3 = (y1 + y2) // 2
    x = int(width * left_cursor / scale / frame_count)
    if left_cursor != -1:
        points = np.array( [(x,y2), (x,y1), (x+5,y3)] )
        cv2.drawContours(image, [points], 0, (0,0,255), -1)
    x = int(width * right_cursor / scale / frame_count)
    if right_cursor != frame_count:
        points = np.array( [(x,y2), (x,y1), (x-5,y3)] )
        cv2.drawContours(image, [points], 0, (0,0,255), -1)
    for mark in bookmarks:
        x = int(width * mark / scale / frame_count)
        points = np.array( [(x,y1), (x+5,y3), (x,y2), (x-5,y3)] )
        cv2.drawContours(image, [points], 0, (0,160,160), -1)
    

def on_mouse(event, x, y, a, b):
    global rewind, mouse_hold, is_playing, was_playing_before_hold, frame_count
    #print(event)
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_hold = True
        was_playing_before_hold = is_playing
        is_playing = False
    if mouse_hold:
        rewind = int(x * frame_count * scale / width)
        if rewind < 0:
            rewind = 0
        if rewind > frame_count:
            rewind = frame_count - 1
        is_playing = False
    if event == cv2.EVENT_LBUTTONUP:
        mouse_hold = False
        if was_playing_before_hold: 
            is_playing = True

next_time = 0

def pause(fps):
    global next_time
    current_time = time.time()
    if current_time < next_time:
        while current_time < next_time:
            current_time = time.time()
        increment = 1
    else:
        increment = int((current_time - next_time)*fps) + 1
    if next_time == 0:
        increment = 1
    next_time = next_time + increment / fps
    return increment

window_name = path_split[-1]
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, on_mouse)



while True:
    
    increment = pause(fps)
    
    if rewind != -1:
        position = rewind
        rewind = -1

    
    vcap.set(cv2.CAP_PROP_POS_FRAMES, position)
    result, image = vcap.read()

    if result:
        image = cv2.resize(image, (width//scale, height//scale))
    else:
        image = prev_image
    image_out = np.concatenate((image, np.zeros((bar_h,width//scale,3),dtype='uint8')))
    prev_image = image
    
    draw_bar(image_out, position)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.imshow(window_name, image_out)
    
    if position == right_cursor and is_playing_selection:
        is_playing_selection = False
        is_playing = False

    if position >= frame_count - increment:
        is_playing = False
        
    if is_playing:
        #print(increment)
        position += increment
    
    k = cv2.waitKeyEx(1)
    if k != -1:
        is_playing_selection = False
    if k == 27: # Esc
        cv2.destroyAllWindows()
        sys.exit(0)
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
    if k == 9: # Tab
        is_playing_selection = True
        is_playing = True
        position = left_cursor
    if k == 13: # Enter
        is_playing_selection = False
        is_playing = False
        save_selection()
    if k == 116: # 'T'
        bookmarks = add_mark(bookmarks, position)
#    if k != -1:
#        print(k)
    
    if cv2.getWindowProperty(window_name,0) < 0:
       break

cv2.destroyAllWindows()
