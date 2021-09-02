import numpy as np
import serial
import serial.tools.list_ports
import crc8
import time

def crc8(crc, a):
    crc ^= a
    for i in range(8):
        if crc & 128:
            crc = np.uint8((crc << 1) ^ 213)
        else:
            crc = np.uint8(crc << 1)
    return crc


def crc8_sbuf(buf):
    crc = 0
    for b in buf:
        crc = crc8(crc, b)
    return crc


buffer = np.array([200, 10, 8, 0, 254, 0,0,0,0,0,0, 180], dtype='uint8')

with serial.Serial('/dev/cu.usbserial-A50285BI', baudrate=400000) as ser:
    for voltage in range(254,200,-1):
        buffer[4] = voltage
        buffer[-1] = crc8_sbuf(buffer[2:-1])
        print(buffer)
        ser.write(buffer.tobytes())
        time.sleep(0.2)
