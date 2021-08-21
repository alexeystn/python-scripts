import wave
import numpy as np
from matplotlib import pyplot as plt

#### Trim wave file

##w_in = wave.open('input.wav', mode='rb')
##w_out = wave.open('trim.wav', mode='wb')
##w_out.setparams(w_in.getparams())
##w_out.writeframes(w_in.readframes(30000))
##w_out.close()
##w_in.close()



def load_sound(filename):
    
    w = wave.open('input/'+filename, mode='rb')
    #print(w.getparams())
    d = w.readframes(w.getnframes())
    w.close()
    
    return np.frombuffer(d, 'int16')[::2]


def plot(arr):
    plt.plot(arr)
    plt.show()


prepare_time = 8 # sec
breath_time = 100 # sec
pause_time = 20 # sec
cycle_count = 4 # times
margin_time = 20
breath_frequency = 13 # 1/min
sampling_frequency = 22050 # Hz

sound_start = load_sound('insert.wav')
sound_stop = load_sound('remove.wav')
sound_tick = load_sound('tick.wav')
sound_final = load_sound('finish.wav')

length_sec = (breath_time + pause_time) * cycle_count + \
              prepare_time + margin_time

time = np.arange(0, length_sec, 1/sampling_frequency)



timestamps_tick = np.arange(0, breath_time, 60/breath_frequency/4)
timestamps_tick = np.array([(timestamps_tick + (breath_time+pause_time)*i + prepare_time)
                            for i in range(cycle_count)])
timestamps_tick = timestamps_tick.flatten()


timestamps_start = np.arange(0, length_sec, (breath_time + pause_time))[:cycle_count] + prepare_time
timestamps_stop  = np.arange(breath_time, length_sec, (breath_time + pause_time))[:cycle_count] + prepare_time
timestamps_final = np.array([(breath_time + pause_time) * cycle_count + prepare_time + 1])


samples_tick  = (timestamps_tick  * sampling_frequency).astype('int')
samples_start = (timestamps_start * sampling_frequency).astype('int')
samples_stop  = (timestamps_stop  * sampling_frequency).astype('int')
samples_final = (timestamps_final * sampling_frequency).astype('int')

sound_full = np.zeros((len(time), 1), dtype='int16')

for s in samples_tick:
    sound_full[s:s+len(sound_tick),0] += sound_tick
    
for s in samples_start:
    sound_full[s:s+len(sound_start),0] += sound_start

for s in samples_stop:
    sound_full[s:s+len(sound_stop),0] += sound_stop

for s in samples_final:
    sound_full[s:s+len(sound_final),0] += sound_final


filename = 'timer_p{4}_b{1}_p{2}_c{3}_f{0}.wav'.format(breath_frequency, breath_time, pause_time, cycle_count, prepare_time)


w = wave.open(filename, mode='wb')
w.setframerate(22050)
w.setsampwidth(2)
w.setnchannels(1)

#w.setparams(params=(nchannels=2, sampwidth=2, framerate=22050, comptype='NONE', compname='not compressed'))
w.writeframes(sound_full)
w.close()

# nchannels, sampwidth, framerate, nframes, comptype, compname





