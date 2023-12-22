import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks, medfilt
import os


def prepare_fir_lpf(fir_length, sample_rate, cutoff_frequency,
                    verbose=False):
    fft_freq = np.fft.fftfreq(fir_length, 1/sample_rate)
    fft_target = np.zeros((fir_length,))
    fft_target[np.abs(fft_freq) < cutoff_frequency] = 1
    fir = np.real(np.fft.ifft(fft_target))
    fir = np.fft.fftshift(fir) * np.hanning(fir_length)
    if verbose:
        plt.figure()
        plt.subplot(211)
        plt.plot(fir)
        plt.title('FIR LPF')
        plt.subplot(212)
        plt.plot(fft_freq[:fir_length//2],
                 np.abs(np.fft.fft(fir))[:fir_length//2])
        plt.xlabel('Frequency, Hz')
        plt.ylabel('Gain')
        
    return fir


def extend_edges(array, n):
    
    left_part = array[:n]
    right_part = array[-n:]
    result = np.hstack((left_part[::-1], array, right_part[::-1]))
    return result


def find_all_peaks(array, threshold_distance=15):

    peaks_high, _ = find_peaks(array)
    peaks_low, _ = find_peaks(-array)
    peaks_all = np.hstack((peaks_high, peaks_low))
    peaks_all = np.sort(peaks_all)
    distances = np.diff(peaks_all)
    shortest_intervals_idx, _ = find_peaks(-distances, height=-threshold_distance)
    removed_idx = np.hstack((shortest_intervals_idx, shortest_intervals_idx+1))
    peaks_all = np.delete(peaks_all, removed_idx)
    return peaks_all

def get_breath_rate(peaks, sample_rate):

    fir_len = 6  # even number: 2, 4 ,6
    fir = np.ones((fir_len,))/fir_len
    rate = sample_rate / np.diff(peaks)
    rate = extend_edges(rate, fir_len//2)
    rate = np.convolve(rate, fir, mode='valid')
    return rate
    

def plot_file(filename):

    data = np.genfromtxt(filename, delimiter=',')
    channels = data[:, 1:]
    breath = data[:, 0]

    sample_rate = 30
    t = np.arange(len(data)) / sample_rate
    
    bias_lpf_cutoff = 0.1
    bias_fir_length = 512
    bias_fir = prepare_fir_lpf(bias_fir_length, sample_rate,
                               bias_lpf_cutoff, False)
    breath_extended = extend_edges(breath, bias_fir_length//2)
    breath_bias = np.convolve(breath_extended, bias_fir, mode='valid')
    breath_no_bias = breath - breath_bias[:-1]

    smooth_lpf_cutoff = 1
    smooth_fir_length = 32
    smooth_fir = prepare_fir_lpf(smooth_fir_length, sample_rate,
                                 smooth_lpf_cutoff, False)
    breath_smooth = np.convolve(breath_no_bias, smooth_fir, mode='same')

    breath_scaled = breath_smooth/np.std(breath_smooth)*200 + 2500
    
    peaks_idxs = find_all_peaks(breath_smooth)

    breath_rate = get_breath_rate(peaks_idxs, sample_rate)

    plt.plot(t, channels)
    plt.plot(t, breath_scaled)
    plt.plot(t[peaks_idxs], breath_scaled[peaks_idxs], 'rx')
    plt.plot(t[peaks_idxs], breath_rate*1000, '.-k')

    plt.show()


if __name__ == '__main__':

    path = './logs/'
    files = [f for f in os.listdir(path) if f.endswith('csv') ]
    filename = path + sorted(files)[-4]
    plot_file(filename)
    plt.show()





