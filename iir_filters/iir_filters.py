import numpy as np
from matplotlib import pyplot as plt

samplingFrequency = 44100

# https://github.com/dimtass/DSP-Cpp-filters/

class Filter:

    def __init__(self, filterType, fc, gain=0, Q=1):

        fs = samplingFrequency
        recalculateCoefs = False
        
        if filterType == 'LPF':
            th = 2.0 * np.pi * fc / fs
            g = np.cos(th) / (1.0 + np.sin(th))
            a0 = (1.0 - g) / 2.0
            a1 = (1.0 - g) / 2.0
            a2 = 0.0
            b1 = -g
            b2 = 0.0

        elif filterType == 'HPF':
            th = 2.0 * np.pi * fc / fs
            g = np.cos(th) / (1.0 + np.sin(th))
            a0 = (1.0 + g) / 2.0
            a1 = -((1.0 + g) / 2.0)
            a2 = 0.0
            b1 = -g
            b2 = 0.0

        elif filterType == 'HPF_BW':
            c = np.tan(np.pi*fc / fs);
            a0 = 1.0 / (1.0 + np.sqrt(2)*c + c**2);
            a1 = -2.0 * a0
            a2 = a0
            b1 = 2.0 * a0*(c**2 - 1.0)
            b2 = a0 * (1.0 - np.sqrt(2)*c + c**2)

        elif filterType == 'LPF_BW':
            c = 1.0 / (np.tan(np.pi*fc / fs))
            a0 = 1.0 / (1.0 + np.sqrt(2)*c + c**2.0)
            a1 = 2.0 * a0
            a2 = self.a0
            b1 = 2.0 * a0*(1.0 - c**2.0)
            b2 = self.a0 * (1.0 - np.sqrt(2)*c + c**2)

        elif filterType == 'BPF_BW':
            c = 1.0 / (np.tan(np.pi*fc/Q / fs))
            d = 2.0 * np.cos(2.0 * np.pi * fc / fs)
            a0 = 1.0 / (1.0 + c)
            a1 = 0.0
            a2 = -a0
            b1 = -a0 * (c * d)
            b2 = a0 * (c - 1.0)
            
        elif filterType == 'BSF_BW':
            c = np.tan(np.pi*fc/Q / fs);
            d = 2.0 * np.cos(2.0 * np.pi * fc / fs)
            a0 = 1.0 / (1.0 + c)
            a1 = -a0 * d
            a2 = a0
            b1 = -a0 * d
            b2 = a0 * (1.0 - c)

        elif filterType == 'LOW_SHELF':
            gain_db = gain
            th = 2.0 * np.pi * fc / fs
            m = 10.0**(gain_db/ 20.0)
            b = 4.0 / (1.0 + m)
            d = b * np.tan(th / 2.0)
            g = (1.0 - d) / (1.0 + d)
            a0 = (1.0 - g) / 2.0
            a1 = a0
            a2 = 0.0    ## FIX
            b1 = -g
            b2 = 0.0
            c0 = m - 1.0
            d0 = 1.0
            recalculateCoefs = True

        elif filterType == 'HIGH_SHELF':
            gain_db = gain
            th = 2.0 * np.pi * fc / fs
            m = 10.0**(gain_db/ 20.0)
            b = (1.0 + m) / 4
            d = b * np.tan(th / 2.0)
            g = (1.0 - d) / (1.0 + d)
            a0 = (1.0 + g) / 2.0
            a1 = -(1.0 + g) / 2.0
            a2 = 0.0    ## FIX
            b1 = -g
            b2 = 0.0
            c0 = m - 1.0
            d0 = 1.0
            recalculateCoefs = True

        elif filterType == 'PARAMETRIC':
            gain_db = gain
            fc /= 2  # ??
            K = 2.0 * np.pi * fc / fs;
            V0 = 10.0 ** (gain_db / 20.0)
            d0 = 1.0 + K/Q + K**2
            a = 1.0 + (V0*K)/Q + K**2
            b = 2.0*(K**2 - 1.0);
            g = 1.0 - (V0*K)/Q + K**2;
            d = 1.0 - K/Q + K**2;
            a0 = a/d0
            a1 = b/d0
            a2 = g/d0
            b1 = b/d0
            b2 = d/d0
            c0 = 1.0
            d0 = 0.0 
            recalculateCoefs = True

        else:
            print('Filter type not specified')

        if recalculateCoefs:
            self.a0 = c0*a0+d0
            self.a1 = c0*a1+d0*b1
            self.a2 = c0*a2+d0*b2
        else:
            self.a0 = a0
            self.a1 = a1
            self.a2 = a2        
        self.b1 = b1
        self.b2 = b2

        
    def apply(self, inputValue):

        x = inputValue
        y = self.a0*x + self.a1*self.x1 + self.a2*self.x2 -\
            self.b1*self.y1 - self.b2*self.y2
        self.x2 = self.x1
        self.x1 = x
        self.y2 = self.y1
        self.y1 = y
        return y

    def reset(self):
        
        self.x1, self.x2 = 0, 0
        self.y1, self.y2 = 0, 0


##for param in [100, 333, 1000, 3333]:
##    f = Filter('PARAMETRIC', fc=param, gain=6)
##for param in [-6, -3, 0, 3, 6]:
##    f = Filter('PARAMETRIC', 1000, gain=param)
##for param in [0.5, 1, 2]:
##    f = Filter('PARAMETRIC', 1000, gain=6, Q=param)
##for param in [100, 333, 1000, 3333]:
##    #f = Filter('LOW_SHELF', fc=param, gain=3)
##    #f = Filter('LOW_SHELF', fc=param, gain=3)
##for param in [-6, -3, 0, 3, 6]:
##    f = Filter('HIGH_SHELF', 1000, gain=param)
##for param in [0.5, 1, 2]:
##    f = Filter('BSF_BW', 1000, Q=param)
for param in [100, 333, 1000, 3333]:
    f = Filter('HPF', fc=param)

    frequencies = np.logspace(np.log10(20), np.log10(20000), 27)
    t = np.arange(samplingFrequency) / samplingFrequency
    response = np.zeros((len(frequencies),))

    for iFr, freq in enumerate(frequencies):
        f.reset()
        inputSignal = np.sin(2 * np.pi * freq * t)
        outputSignal = np.zeros(len(inputSignal))
        for iSmp, x in enumerate(inputSignal):
            outputSignal[iSmp] = f.apply(x)
        result = outputSignal[len(outputSignal)//2:].max()
        response[iFr] = result

    plt.plot(frequencies, response)

plt.grid(True)
plt.gca().set_xscale('log')
plt.gca().set_yscale('log')
plt.show()














    
