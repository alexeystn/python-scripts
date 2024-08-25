import serial
import time
import crsf
import numpy as np
import cv2

port = '/dev/tty.usbserial-FTVOZKY70'

rc_data = [0, 0, -100, 0] + [-100] * 12

armed = 0
throttle = 0
yaw = 0
yaw_scale = 10
yaw_reset_time = 0
max_throttle = 30

img = np.ones((320, 320), dtype='uint8') * 127

fps_counter = 0
fps_prev_time = 0

with serial.Serial(port, 400000) as ser:
    while True:

        cv2.imshow('RC', img)
        k = cv2.waitKey(1)

        if k == 27:
            break

        if k == 32:
            armed ^= 1
            print('Arm: {0}'.format(armed))

        if k == 119:
            if throttle < max_throttle and armed:
                throttle += 1
                print('Throttle: {0}'.format(throttle))

        if k == 115:
            if throttle > 0:
                throttle -= 1
                print('Throttle: {0}'.format(throttle))
        
        if k == 100:
            yaw = 1
            print('Yaw Right')
            yaw_reset_time = time.time() + 0.5

        if k == 97:
            yaw = -1
            print('Yaw Left')
            yaw_reset_time = time.time() + 0.5

        # Throttle
        rc_data[2] = (throttle / max_throttle) * 200 - 100

        # Yaw
        if yaw != 0:
            if time.time() > yaw_reset_time:
                yaw = 0
        rc_data[3] = yaw * yaw_scale    

        # Arm state
        if armed:
            rc_data[4] = 100
        else:
            rc_data[4] = -100
            throttle = 0

        packet = crsf.build_packet(rc_data)
        ser.write(bytes(packet))
        ser.flush()

        t = int(time.time())
        if t != fps_prev_time:
            fps_prev_time = t
            print(fps_counter, 'FPS')
            fps_counter = 0
        fps_counter += 1

        
    
cv2.destroyAllWindows()
