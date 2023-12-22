import datetime
import numpy as np
import hid # pip3 install hidapi
import serial
import serial.tools.list_ports
import plot_hid_com

VENDOR_ID = 0x1209
PRODUCT_ID = 0x4F54
COM_PORT = 'COM5'

def list_hid_devices():
    print('HID devices')
    for device in hid.enumerate():
        print('0x{0:04x}:0x{1:04x} {2}'.format(
              device['vendor_id'],
              device['product_id'],
              device['product_string']
              ))
    print()

def list_com_ports():
    print('COM ports:')
    for port in serial.tools.list_ports.comports():
        print(port.device)
    print()


def parse_hid_report(report):
    report_np = np.array(report)
    channels = report_np[4::2]*256 + report_np[3::2]
    return channels


def main():

    list_hid_devices()
    list_com_ports()
    
    opentx_radio = hid.device()
    opentx_radio.open(VENDOR_ID, PRODUCT_ID)
    opentx_radio.set_nonblocking(True)
    
    breath_sensor = serial.Serial(port=COM_PORT, timeout=10)

    date_time = datetime.datetime.now()
    filename = './logs/' + date_time.strftime('%Y%m%d_%H%M%S.csv')
    
    file = open(filename, 'w')
    
    counter = 0
    
    while True:
        try:
            line = breath_sensor.readline().decode().strip()
            report = opentx_radio.read(64)
            if report:
                counter += 1
                channels = parse_hid_report(report)
                output_line = line + ',' +\
                              ','.join([str(ch) for ch in channels[:4]]) + '\n'
                file.write(output_line)
                if counter == 5:
                    counter = 0
                    print(output_line, end='')
        except KeyboardInterrupt:
            break

    file.close()
    print('Done')

    plot_hid_com.plot_file(filename)


if __name__ == '__main__':
    main()


