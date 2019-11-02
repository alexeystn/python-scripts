import cv2
import numpy as np
import time

input_filename = '/Users/imac/Desktop/PICT0105.AVI'
output_filename = 'Resize_' + input_filename.split(sep='/')[-1] + '.mp4'

start_time = 0*60 + 36
stop_time = 0*60 + 55

output_width = 640
output_height = 480


def generate_map(width, height):

    map_x = np.tile(np.arange(width), (height, 1)).astype(np.float32)
    map_y = np.tile(np.arange(height), (width, 1)).astype(np.float32).T

    map_x_shift = 0;
    map_y_shift = 0; 
    map_x_shift = (np.sin((map_x/(width-1)-0.5)*2*np.pi)/np.pi/6) * width
    map_y_shift = (map_y/(height-1)-0.5) * (np.cos((map_x/(width-1)-0.5)*np.pi)/2-0.5) * height / 2
    
    map_x += map_x_shift
    map_y += map_y_shift
    
    return map_x, map_y

video_capture = cv2.VideoCapture(input_filename)

width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = round(video_capture.get(cv2.CAP_PROP_FPS))
frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

start_frame = round(fps*start_time)
if stop_time:
    stop_frame = round(fps*stop_time)
else:
    stop_frame = frame_count

map_x, map_y = generate_map(width, height)

video_writer = cv2.VideoWriter(output_filename,
                               cv2.VideoWriter_fourcc(*"h264"),
                               fps,
                               (output_width, output_height))

video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

video_writer.set(cv2.VIDEOWRITER_PROP_QUALITY, 100)

t1 = time.time()

for frame in range(start_frame, stop_frame):
    result, image = video_capture.read()
    #image = cv2.remap(np.array(image), map_x, map_y, cv2.INTER_LINEAR)
    image = cv2.resize(image, (output_width, output_height), cv2.INTER_CUBIC)
    video_writer.write(image)
    if frame % 10 == 0:
        print('{0:.2f}%'.format((frame - start_frame)/(stop_frame - start_frame)*100))
        
video_writer.release()

t2 = time.time()

print('Converted in {0:.1f}s'.format(t2-t1))


