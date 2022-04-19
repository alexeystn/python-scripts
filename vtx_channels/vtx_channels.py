import numpy as np
from itertools import combinations

# Check results here: http://etserv.etheli.com/IMDTabler/run

pilots_count = 6
lowest_lowband_channel = 6


table = {'R': [5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917],
         'L': [5362, 5399, 5436, 5473, 5510, 5547, 5584, 5621]}

available_frequencies = table['L'][(lowest_lowband_channel-1):] + table['R']


def get_channel_label(freq):
    result = 'XX'
    for band in table.keys():
        for channel in range(8):
            if freq == table[band][channel]:
                result = band + str(channel+1)
    return result


def calculate_imd_frequencies(freq_set):
    imd_freq_set = np.zeros((len(freq_set), len(freq_set), 2))
    for i1, freq_1 in enumerate(freq_set):
        for i2, freq_2 in enumerate(freq_set):
            imd_freq_set[i1, i2, 0] = 2*freq_1 - freq_2
            imd_freq_set[i1, i2, 1] = 2*freq_2 - freq_1
        imd_freq_set[i1, i1, :] = 0
    return set(imd_freq_set.flatten())


def check_mutual_distance(freq_set_1, freq_set_2):
    distance = np.zeros((len(freq_set_1), len(freq_set_2)))
    for i1, freq_1 in enumerate(freq_set_1):
        for i2, freq_2 in enumerate(freq_set_2):
            distance[i1, i2] = freq_1 - freq_2
    return np.min(np.abs(distance).flatten())


for pilots_frequencies in combinations(available_frequencies, pilots_count):

    imd_frequencies = calculate_imd_frequencies(pilots_frequencies)
    imd_min_distance = check_mutual_distance(pilots_frequencies, imd_frequencies)
    if imd_min_distance < 37:
        continue

    labels_string = '   '.join([get_channel_label(freq) for freq in pilots_frequencies])
    frequencies_string = ' '.join([str(freq) for freq in pilots_frequencies])

    print(labels_string)
    print(frequencies_string)
    print()
