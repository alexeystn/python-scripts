import hid # pip3 install hidapi
import numpy as np
import time
import datetime

# Show list of all HID devices:
for device in hid.enumerate():
    print('0x{0:04x}:0x{1:04x} {2}'.format(
          device['vendor_id'],
          device['product_id'],
          device['product_string']))


class FileWriter:

    delay = 2
    started = False
    f = None

    def start(self):
        if not self.started:
            self.started = True
            d = datetime.datetime.now()
            filename = d.strftime('%Y%m%d_%H%M%S.csv')
            self.f = open('./logs/' + filename, 'w')
            print('Start')

    def stop(self):
        if self.started:
            self.f.close()
            self.started = False
            print('Stop')

    def write(self, report):
        if self.started:
            string = ','.join([str(i) for i in report]) + '\n'
            self.f.write(string)

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
