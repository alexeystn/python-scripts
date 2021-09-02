import numpy as np
from matplotlib import pyplot as plt

# Log format example:
# "Async Serial","data",0.0006025,2.375e-05,0xC8

uart_bytes = []
uart_timestamps = []

with open('./capture/decoded_crsf.csv', 'r') as f:
    f.readline()
    for line in f:
        split_line = line.split(sep=',')
        uart_timestamps.append(int(float(split_line[2])*1e6))
        uart_bytes.append(int(split_line[4],16))

packets = []
packet_timestamps = []

for i in range(len(uart_bytes)):
    if uart_bytes[i] == 200: # 0xC8 = CRSF_SYNC_BYTE
        length = uart_bytes[i+1]
        packet = uart_bytes[(i+2):(i+length+2)]
        packets.append(packet)
        packet_timestamps.append(uart_timestamps[i+length+1]) # +1 ???
        i += length

rc_data = []
rc_timestamps = []

for packet, timestamp in zip(packets, packet_timestamps):
    if packet[0] == 22: # 0x16 = CRSF_FRAMETYPE_RC_CHANNELS_PACKED
        packet = packet[1:-1] # remove type and crc
        packet_bin_8 = ['{0:08b}'.format(i)[::-1] for i in packet] # [::-1] reverse
        packet_bin_full = ''.join(packet_bin_8)
        packet_bin_11 = [packet_bin_full[11*i:11*(i+1)] for i in range(16)]
        rc_packet = [int(b[::-1],2) for b in packet_bin_11]
        rc_data.append(rc_packet)
        rc_timestamps.append(timestamp)

rc_data = np.array(rc_data)
plt.plot(rc_data)
plt.show()

