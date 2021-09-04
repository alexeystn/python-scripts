import numpy as np
from matplotlib import pyplot as plt


def load_crsf_rx(filename):
    
    # Log format example:
    # "Async Serial","data",0.0006025,2.375e-05,0xC8

    uart_bytes = []
    uart_timestamps = []

    with open(filename, 'r') as f:
        f.readline()  # skip header line
        for line in f:
            split_line = line.split(sep=',')
            uart_timestamps.append(int(float(split_line[2])*1e6))
            uart_bytes.append(int(split_line[4], 16))

    packets = []
    packet_timestamps = []

    for i in range(len(uart_bytes)):
        if uart_bytes[i] == 200:  # 0xC8 = CRSF_SYNC_BYTE
            length = uart_bytes[i+1]
            packet = uart_bytes[(i+2):(i+length+2)]
            packets.append(packet)
            packet_timestamps.append(uart_timestamps[i+length+1])  # +1 ???
            i += length

    rc_data = []
    rc_timestamps = []

    for packet, timestamp in zip(packets, packet_timestamps):
        if packet[0] == 22:  # 0x16 = CRSF_FRAMETYPE_RC_CHANNELS_PACKED
            packet = packet[1:-1]  # remove type and crc
            packet_bin_8 = ['{0:08b}'.format(i)[::-1] for i in packet]  # [::-1] reverse
            packet_bin_full = ''.join(packet_bin_8)
            packet_bin_11 = [packet_bin_full[11*i:11*(i+1)] for i in range(16)]
            rc_packet = [int(b[::-1], 2) for b in packet_bin_11]
            rc_data.append(rc_packet)
            rc_timestamps.append(timestamp)

    rc_data = np.array(rc_data)
    return rc_data, rc_timestamps


def load_tx_switch(filename, edge):

    # Log format example:
    # 0.689994000,0
    # 0.777677250,1
    
    with open(filename, 'r') as f:
        sw_timestamps = []
        f.readline()  # skip header line
        for line in f:
            split_line = line.split(sep=',')
            if int(split_line[1]) == edge:
                sw_timestamps.append(int(float(split_line[0])*1e6))
    return sw_timestamps


def find_rx_switches(rc_data, rc_timestamps, threshold):
    rc_data_diff = np.diff(rc_data)
    idx = np.where((np.abs(rc_data_diff) > threshold) &
                   (np.sign(rc_data_diff) == np.sign(threshold)))[0]
    idx += 1  # next packet is changed
    return np.array([rc_timestamps[i] for i in idx])


channel = 5
sw_toggle_time = load_tx_switch('./capture/switch.csv', 0)
sw_toggle_time = sw_toggle_time[1:]
rx_rc_data, rx_rc_time = load_crsf_rx('./capture/crsf_rx.csv')
rx_time = find_rx_switches(rx_rc_data[:, channel], rx_rc_time, 100)

latency = []
for sw in sw_toggle_time:
    rx = rx_time[np.where(rx_time > sw)[0].min()]
    d = rx - sw
    if d < 50000:  # 50 ms switch chatter
        latency.append(d)
latency = np.array(latency)/1000

mu = np.mean(latency)
sigma = np.std(latency)

text = r'$\mu$={0:.1f} ms, $\sigma$={1:.1f} ms'.format(mu, sigma)
plt.hist(latency, bins=range(3, 10), rwidth=0.85)
plt.grid(axis='y', alpha=1)
plt.xlabel('Latency, ms')
plt.ylabel('Counts')
plt.title('TBS Tracer')
plt.text(6.5, 18, text)
plt.ylim((0, 25))
plt.show()
