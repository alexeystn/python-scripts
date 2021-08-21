import numpy as np
import cv2 as cv
import undistort as ud


input_filename = '/Volumes/HDD/Flights/2020.06.28/YDXJ0127.mp4'
output_filename = 'output.mp4'

start_time = 3*60+12
stop_time = 3*60+58

output_width = 960#640
output_height = 720#480

h = int(1080 / 3 * 4)
w = 1920
    
with open('calib.npy', 'rb') as f:
    mtx = np.load(f)
    dist = np.load(f)


mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, mtx, (w,h), 5)


video_capture = cv.VideoCapture(input_filename)
width = int(video_capture.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(video_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = round(video_capture.get(cv.CAP_PROP_FPS))
frame_count = int(video_capture.get(cv.CAP_PROP_FRAME_COUNT))

start_frame = round(fps*start_time)
stop_frame = round(fps*stop_time)

video_writer = cv.VideoWriter(output_filename,
                               cv.VideoWriter_fourcc(*"h264"),
                               fps,
                               (output_width, output_height))


video_capture.set(cv.CAP_PROP_POS_FRAMES, start_frame)

video_writer.set(cv.VIDEOWRITER_PROP_QUALITY, 100)

for frame in range(start_frame, stop_frame):
    result, img = video_capture.read()

    #image = process(image, mtx, dist)
    img = ud.resize(img)

    img = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

    
    img = cv.resize(img, (output_width, output_height), cv.INTER_CUBIC)
    video_writer.write(img)
    if frame % 10 == 0:
        print('{0:.2f}%'.format((frame - start_frame)/(stop_frame - start_frame)*100))
        
video_writer.release()


