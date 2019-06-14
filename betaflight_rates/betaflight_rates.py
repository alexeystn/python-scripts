import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rc

class Rates:

    def __init__(self, name, rc_rate, super_rate, rc_expo, color):
        self.name = name
        self.rc_rate = rc_rate
        self.super_rate = super_rate
        self.rc_expo = rc_expo
        self.color = color

    def angle_speed(self, com, rate, srate, expo):
        if expo:
            com = com**4 * expo + com * (1 - expo)
        if rate > 2:
            rate = rate + 14.54 * (rate - 2)
        angle = 200 * rate * com
        if srate:
            factor = 1 / (np.clip(1 - (com * srate), 0.01, 1))
            angle *= factor
        return np.clip(angle, 0, 2000)

    def curve(self):
        n = 500
        commands = np.linspace(0, 1, n)
        output = np.zeros((n, 1))
        for i, c in enumerate(commands):
            output[i] = self.angle_speed(c, self.rc_rate, self.super_rate, self.rc_expo)
        return output

    def legend(self):
        m = self.curve()
        s = '{3:12s} {0:.2f}  {1:.2f}  {2:.2f}  ({4:.0f})'. \
            format(self.rc_rate, self.super_rate, self.rc_expo, self.name, m[-1][0])
        return s

rates_list = []

rates_list.append( Rates('Default',    1.00, 0.70, 0.00, 'grey'))

rates_list.append( Rates('HellFly-PR', 0.80, 0.50, 0.20, 'orangered'))
rates_list.append( Rates('HellFly-Y',  0.70, 0.35, 0.15, 'orangered'))

rates_list.append( Rates('Alexey-PR',  0.45, 0.75, 0.15, 'forestgreen'))
rates_list.append( Rates('Alexey-Y',   0.35, 0.70, 0.15, 'forestgreen'))

rates_list.append( Rates('Shvedov-PR', 0.95, 0.80, 0.30, 'dodgerblue'))
rates_list.append( Rates('Shvedov-Y',  1.10, 0.70, 0.30, 'dodgerblue'))


legend = []

for r in rates_list:
    plt.plot(r.curve(), r.color)
    legend.append(r.legend())

rc('font', family='Consolas')
plt.legend(legend, title=' '*11+'rate  super expo')
plt.grid(True)
plt.show()
