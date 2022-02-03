import numpy as np
from matplotlib import pyplot as plt

def apply_betaflight_rates(command, rates):
    # Rate, SuperRate, Expo
    rate = rates[0]
    super_rate = rates[1]
    expo = rates[2]
    com = command.copy()
    if expo:
        com = com * np.abs(com)**3 * expo + com * (1 - expo);
    if rate > 2.0:
        rate += 14.54 * (rate - 2.0);
    angle_rate = 200.0 * rate * com
    if super_rate:
        super_factor = 1.0 / np.clip(1.0 - (np.abs(com) * super_rate), 0.01, 1.00)
        angle_rate *= super_factor
    return angle_rate

def apply_actual_rates(command, rates):
    # CenterSensitivity, MaxRate, Expo
    center = rates[0]
    max_rate = rates[1]
    expo = rates[2]   
    com = command.copy() 
    expo_factor = np.abs(com) * ((com**5) * expo + com * (1-expo))
    stick_movement = max([0, max_rate - center])
    angle_rate = com * center + stick_movement * expo_factor
    return angle_rate

rc_range = np.linspace(-1,1,100)

# rate_bf = apply_betaflight_rates(rc_range, [0.6, 0.7, 0.0])
# rate_act = apply_actual_rates(rc_range, [120, 400, 0.5])

rate_bf = apply_betaflight_rates(rc_range, [0.6, 0.55, 0.0])
rate_act = apply_actual_rates(rc_range, [120, 300, 0.5])

ratio = rate_act / rate_bf
print('{0:.1f}% - {1:.1f}%'.format(min(ratio)*100, max(ratio)*100))

plt.plot( rc_range, rate_bf )
plt.plot( rc_range, rate_act )

plt.grid(True)
plt.show()
