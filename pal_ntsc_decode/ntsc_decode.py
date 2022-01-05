import numpy as np
from matplotlib import pyplot as plt


def find_edges(t, signal, threshold, kind='lead'):
    if type(t) == int:
        t = np.arange(len(signal))
    if kind == 'lead':
        mask = (signal < threshold)[:-1] * (signal >= threshold)[1:]
    else:  # 'trail'
        mask = (signal >= threshold)[:-1] * (signal < threshold)[1:]
    return t[1:][mask]


def is_within_limit(value, limit):
    res = (value >= limit[0]) and (value <= limit[1])
    return res


def filter_video(signal, sample_rate):
    hsync_width = 4.7e-6 # standard
    n = int(np.round(sample_rate * hsync_width) / 1.5)
    fir = (np.cos(np.linspace(-np.pi, np.pi, n)) + 1)/2   
    fir /= np.sum(fir)
    signal_filtered = np.convolve(signal, fir, mode='same')
    return signal_filtered


def find_hsync_points(edges, sample_rate):
    hsync_interval = 63.5e-6 # standard
    diff_edges = np.diff(edges)   
    limit = np.array([0.95, 1.05]) * hsync_interval * sample_rate # ±5%
    mask = np.zeros(edges.shape, dtype='uint8')
    i = 0
    while i < (len(edges) - 1):
        if is_within_limit(diff_edges[i], limit):
            cnt = 0
            while is_within_limit(diff_edges[i], limit):
                cnt += 1
                i += 1
                if i >= (len(edges) - 1):
                    break
            if cnt >= 253: # including
                mask[i-1-240:i-1] = 1 # half-frame 240 lines
        i += 1
    return edges[mask > 0]


def get_line_level(signal, hsync, sample_rate):
    t_start = int(10e-6 * sample_rate) # skip sync pulse and color burst
    t_stop = int(55e-6 * sample_rate) # less than 'hsync_interval'
    line_level = np.zeros((len(hsync),))
    for i, t in enumerate(hsync):
        line_level[i] = np.mean(signal[t + t_start : t + t_stop])
    return line_level


def normalize(signal):
    signal = signal.astype('float')
    signal -= np.min(signal) + 1
    signal /= np.max(signal) * 0.9
    return signal


filename = 'NewFile2.wfm'
sample_rate = 2500000
threshold = 0.15

a = np.fromfile(filename, dtype='uint8')[-12000000:]
signal_video = a[1::2].astype('float')
signal_led = a[0::2].astype('float')

signal_video = normalize(signal_video)
signal_led = normalize(signal_led)

signal_filtered = filter_video(signal_video, sample_rate)
edges_ntsc = find_edges(0, signal_filtered, threshold)

hsync_t = find_hsync_points(edges_ntsc, sample_rate)
level = get_line_level(signal_video, hsync_t, sample_rate)

edges_led = find_edges(0, signal_led, 0.5)
edges_video = find_edges(hsync_t, level, 90)

plt.plot(signal_video, 'b', linewidth=0.5)
#plt.plot(edges, [threshold for e in edges], 'xr')

plt.plot(signal_led, 'm', linewidth=0.5)
#plt.plot(hsync_t, [threshold for i in hsync_t], 'rx')

#plt.plot(edges_led, 'oy'
         
#plt.plot(hsync_t, level, 'gs')
         
plt.show()




##plt.plot(res[1:])
##plt.show()

#plt.plot(d_edges,'.-')
#plt.show()

##plt.figure
##plt.plot(signal_filtered)
##plt.plot(edges, [80 for e in edges], 'ro')
##plt.show()




