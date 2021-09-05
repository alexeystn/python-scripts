import numpy as np
from matplotlib import pyplot as plt
import json
import sys

def load_crsf_rx(filename):
    
    # Log format example:
    # 0.001874500000000,0x18,,

    uart_bytes = []
    uart_timestamps = []

    with open(filename, 'r') as f:
        f.readline()  # skip header line
        for line in f:
            split_line = line.split(sep=',')
            uart_timestamps.append(int(float(split_line[0])*1e6))
            uart_bytes.append(int(split_line[1], 16))

    packets = []
    packet_timestamps = []

    for i in range(len(uart_bytes)):
        if (uart_bytes[i] == 200) or (uart_bytes[i] == 238):  # 0xC8 = CRSF_SYNC_BYTE
            length = uart_bytes[i+1]
            if length != 24:
                continue
            packet = uart_bytes[(i+2):(i+length+2)]
            packets.append(packet)
            try:
                packet_timestamps.append(uart_timestamps[i+length+1])  # +1 ???
            except:
                continue
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


def load_tx_switch(filename):

    # Log format example:
    # 0.689994000,0
    # 0.777677250,1
    
    with open(filename, 'r') as f:
        sw_timestamps = []
        f.readline()  # skip header line
        for line in f:
            split_line = line.split(sep=',')
            if 1: #int(split_line[1]) == edge:
                sw_timestamps.append(int(float(split_line[0])*1e6))
    return sw_timestamps


def filter_tx_switches(sw_timestamps, threshold=10000):
    idx = np.where( np.diff(sw_timestamps) > threshold )[0]
    return [sw_timestamps[i] for i in idx]


def find_rx_switches(rc_data, rc_timestamps, threshold):
    rc_data_diff = np.diff(rc_data)
    idx = np.where(np.abs(rc_data_diff) > threshold)[0]
    idx += 1  # next packet is changed
    return np.array([rc_timestamps[i] for i in idx])


def plot_histogram(values, limits):
    mu = np.mean(latency)
    sigma = np.std(latency)
    text = r'$\mu$={0:.1f} ms, $\sigma$={1:.1f} ms'.format(mu, sigma)
    plt.hist(latency, bins=range(limits[0], limits[1]), rwidth=0.85)
    plt.grid(axis='y', alpha=1)
    plt.xlabel('Latency, ms')
    plt.ylabel('Counts')
    #plt.title('TBS Tracer')
    plt.text(6.5, 18, text)
    plt.show()


def get_latency(sw_toggle_time, rx_time):
    latency = []
    for sw in sw_toggle_time:
        aft = np.where(rx_time > sw)[0]
        if len(aft) > 0:
            rx = rx_time[aft.min()]
        else:
            break
        d = rx - sw
        if 1:#d < 50000:  # 50 ms switch noise
            latency.append(d)
    latency = np.array(latency)/1000
    return latency


    
#sys.exit(0)


configs = ['crossfire50', 'crossfire150', 'tracer250', 'elrs500']
letters = ['a', 'b', 'c']
result = {}

for config in configs:
    conf_latency = []
    for letter in letters:
        config_x = config + letter
        print(config_x)

        channel = 5
        sw_toggle_time = load_tx_switch('./capture/{0}_sw.csv'.format(config_x))
        sw_toggle_time = sw_toggle_time[1:]

        #print(len(sw_toggle_time))
        sw_toggle_time = filter_tx_switches(sw_toggle_time)
        #print(len(sw_toggle_time))
        rx_rc_data, rx_rc_time = load_crsf_rx('./capture/{0}_rx.csv'.format(config_x))
        rx_time = find_rx_switches(rx_rc_data[:, channel], rx_rc_time, 100)
        tx_rc_data, tx_rc_time = load_crsf_rx('./capture/{0}_tx.csv'.format(config_x))
        tx_time = find_rx_switches(tx_rc_data[:, channel], tx_rc_time, 100)
        
        #print(len(rx_time))
        #latency = get_latency(sw_toggle_time, rx_time)
        latency = np.array(rx_time - tx_time[:len(rx_time)])/1000

        conf_latency.append(latency)
    conf_latency = np.hstack(conf_latency)
    result[config] = list(conf_latency)
    print(config_x)

a_file = open("data.json", "w")
json.dump(result, a_file)
a_file.close()




#plot_histogram(latency, (0, 40))
