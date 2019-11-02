import serial
import time

import serial.tools.list_ports

def find_com_port():
    for comport in serial.tools.list_ports.comports():
        if 'modem' in comport.device:
            return comport.device
    return 0


def get_diff(comport, filename):
    with open(filename, 'w') as out:
        with serial.Serial(comport, 115200, timeout=1) as ser:
            ser.write(b'#cli\r\n')
            time.sleep(1)
            ser.reset_input_buffer()
            ser.write(b'diff all\r\n')
            ser.readline()
            while True:
                line = ser.readline()
                if not line:
                    break
                if len(line) <= 2 or line[0] == ord('#'):
                    continue
                print(line.decode()[:-2])
                out.write(line.decode())


def put_diff(comport, filename):
    with open(filename, 'r') as inp:
        with serial.Serial(comport, 115200, timeout=2) as ser:
            ser.write(b'#cli\r\n')
            time.sleep(1)
            for line in inp:
                ser.write(line.encode('utf-8'))
                print (ser.readline().decode()[:-2])
                
            while ser.in_waiting:
                print (ser.readline().decode()[:-2])


port = find_com_port()



if port:
    get_diff(port, '20190723_Yellow.txt')
    #put_diff(port, 'dys.txt')
else:
    print('Port not availible')

    
