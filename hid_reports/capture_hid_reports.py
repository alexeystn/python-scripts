import hid # pip3 install hidapi
import numpy as np
import time

# Show list of all HID devices:
for device in hid.enumerate():
    print('0x{0:04x}:0x{1:04x} {2}'.format(
          device['vendor_id'],
          device['product_id'],
          device['product_string']))

# Put your radio IDs here:
vendor_id = 0x1209
product_id = 0x4f54

opentx_radio = hid.device()
opentx_radio.open(vendor_id, product_id)
opentx_radio.set_nonblocking(True)

capture_length = 5000
report_max_size = 64

capture = np.zeros((capture_length,report_max_size), dtype='uint8')
timestamps = np.zeros((capture_length,))

cnt = 0
while True:
    report = opentx_radio.read(report_max_size)
    if report:
        timestamps[cnt] = time.time()
        capture[cnt,:len(report)] = report
        cnt += 1
        #if cnt % 50 == 0:
              #print('.')
        if cnt == capture_length:
            break

periods = np.diff(timestamps)
frequency = 1/np.median(periods)
np.savez('capture.npz', timestamps=timestamps, capture=capture)

print('HID report frequency: {0:.1f} Hz'.format(frequency))


      
