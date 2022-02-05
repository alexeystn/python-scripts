import time
import sys
import os
import datetime
import numpy as np
import hid # pip3 install hidapi


VENDOR_ID = 0x1209
PRODUCT_ID = 0x4F54


def list_hid_devices():
    for device in hid.enumerate():
        print('0x{0:04x}:0x{1:04x} {2}'.format(
              device['vendor_id'],
              device['product_id'],
              device['product_string']
              ))


def analyze_file(filename):
    fs = 500
    # cutoff = 30
    n = 11
    # desired = (1,1,0,0)
    # bands = (0, cutoff*0.5, cutoff*1.5, fs/2)
    # fir = signal.firls(n, bands, desired, nyq=fs/2)
    fir = np.ones((n,))/n
    rc_data = np.genfromtxt(filename, delimiter=',')
    throttle_channel = 2
    throttle = rc_data[:,throttle_channel] / 2048 * 100
    mask = np.where(throttle > 10)[0]
    if len(mask) == 0:
        print('===== No data')
        return
    throttle = throttle[mask[0]:mask[-1]]
    throttle = np.convolve(throttle, fir, mode='valid')

    throttle_diff = np.abs(np.diff(throttle))*fs
    result = np.mean(throttle_diff)
    print('===== {0:.0f}%'.format(result))

    
class HIDCapturer:

    stop_delay = 2
    start_delay = 2 
    output_path = './logs/'

    def __init__(self, trig_ch, thr_ch):
        self.trigger_channel = trig_ch - 1
        self.throttle_channel = thr_ch - 1
        self.start_time = 0
        self.prev_trigger_state = False
        self.last_throttle_time = 0
        self.started = False
        self.file = None
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

    def start(self):
        self.started = True
        d = datetime.datetime.now()
        filename = self.output_path + d.strftime('%Y%m%d_%H%M%S.csv')
        self.file = open(filename, 'w')
        self.filename = filename
        print('Start')

    def stop(self):
        self.file .close()
        self.started = False
        print('Stop')
        analyze_file(self.filename)

    def write(self, report):
        
        if report[self.throttle_channel] > 10:
            self.last_throttle_time = time.time()
        
        if self.started:
            string = ','.join([str(i) for i in report]) + '\n'
            self.file.write(string)
            if report[self.throttle_channel] < 10:
                if (time.time() - self.last_throttle_time > self.stop_delay) \
                and self.last_throttle_time:
                    self.stop()
        else:
            trigger_state = report[self.trigger_channel] > 2000
            if trigger_state and not self.prev_trigger_state:
                self.start_time = time.time() + self.start_delay
            self.prev_trigger_state = trigger_state
            if time.time() > self.start_time and self.start_time:
                self.start_time = 0
                self.last_throttle_time = time.time()
                self.start()


def parse_hid_report(report):
    report_np = np.array(report)
    channels = report_np[4::2]*256 + report_np[3::2]
    return channels


def main():

    # list_hid_devices()
    opentx_radio = hid.device()
    opentx_radio.open(VENDOR_ID, PRODUCT_ID)
    opentx_radio.set_nonblocking(True)

    hcap = HIDCapturer(trig_ch=6, thr_ch=3)
    print('Ready')

    try:
        while True:
            report = opentx_radio.read(64)
            if report:    
                channels = parse_hid_report(report)
                hcap.write(channels)

    except KeyboardInterrupt:
        hcap.stop()


if __name__ == '__main__':
    main()


