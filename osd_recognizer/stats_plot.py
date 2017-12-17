import matplotlib.pyplot as plt


f = open('stats_.txt', 'r')

alt = []


for s in f:
    try:
        n = int(s)
    except:
        pass
    else:
        alt.append(n)

plt.plot(alt)
plt.show()
    
f.close()


