import hid # pip3 install hidapi
import numpy as np
import time
import datetime
from scipy import signal

# Show list of all HID devices:
for device in hid.enumerate():
    print('0x{0:04x}:0x{1:04x} {2}'.format(
          device['vendor_id'],
          device['product_id'],
          device['product_string']))


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
    throttle = throttle[mask[0]:mask[-1]]
    throttle = np.convolve(throttle, fir, mode='valid')

    throttle_diff = np.abs(np.diff(throttle))*fs
    result = np.mean(throttle_diff)
    print('{0:.1f}%'.format(result))
    

class FileWriter:

    delay = 2
    started = False
    f = None
    last_throttle_time = 0

    def start(self):
        if not self.started:
            self.started = True
            d = datetime.datetime.now()
            filename = './logs/' + d.strftime('%Y%m%d_%H%M%S.csv')
            self.f = open(filename, 'w')
            self.filename = filename
            print('Start')

    def stop(self):
        if self.started:
            self.f.close()
            self.started = False
            print('Stop')
            self.last_throttle_time = 0
            analyze_file(self.filename)

    def write(self, report):
        if self.started:
            string = ','.join([str(i) for i in report]) + '\n'
            self.f.write(string)
            if report[2] < 10:
                if time.time() - self.last_throttle_time > self.delay and self.last_throttle_time:
                    self.stop()
            else:
                self.last_throttle_time = time.time()
            

# Put your radio IDs here:
vendor_id = 0x1209
product_id = 0x4f54
opentx_radio = hid.device()
opentx_radio.open(vendor_id, product_id)
opentx_radio.set_nonblocking(True)

report_max_size = 64
cnt = 0

trigger_channel = 5

trigger_state = False
trigger_state_prev = False

start_time = 0

f = FileWriter()

try:
    while True:
        report = opentx_radio.read(report_max_size)
        if report:
            report_np = np.array(report)
            channels = report_np[4::2]*256 + report_np[3::2]
            f.write(channels)

            trigger_state = channels[trigger_channel] > 2000
            if trigger_state and not trigger_state_prev:
                f.stop()
                start_time = time.time() + f.delay
            trigger_state_prev = trigger_state
            
            if start_time and time.time() > start_time:
                start_time = 0
                f.start()

except KeyboardInterrupt:
    f.stop()
