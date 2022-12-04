import numpy as np
from matplotlib import pyplot as plt

results = {
    1: 83,
    2: 93,
    3: 137,
    4: 86,
    5: 62,
    6: 70,
    'help': 67,
    'other': 915
    }

def succeeded_part(n):
    succesfull_students = [results[i] for i in range(1, 1+n)]
    attempted_students = [results[i] for i in range(1, 1+6)]
    part = sum(succesfull_students) / sum(attempted_students)
    return part


attempts = []
passed = []

for i in range(1,7):
    attempts.append(i)
    passed.append(succeeded_part(i)*100)
    print( '{0}: {1:.0f}%'.format(i, succeeded_part(i)*100))

plt.plot(attempts, passed, 'd-')
plt.ylim((-10,110))
plt.grid(True)
plt.xlabel('Попытка')
plt.ylabel('% сдавших')
plt.show()
