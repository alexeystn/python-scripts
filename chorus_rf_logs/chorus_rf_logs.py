import os

path = '/Volumes/HD/Flights/2018.10.07/Chorus/'
files = os.listdir(path)


files.sort()

pilot_name = 'Alexey'

ff = open(pilot_name + '.txt', 'w');
    
for filename in files:
    f = open(path + filename);

    header = True
    pause = False
    for s in f:

        output = ''
        
        if header:
            header = False
            continue
        
        line = s.split(sep =',')
        name = line[1]
        time = line[4]
        
        t_min = int(time[0])
        t_sec = int(time[2:4])
        t_msec = int(time[5:8])
        t = t_min * 60 + t_sec + t_msec/1000

        s = s[:-1]

        if name == pilot_name:
            if (t > 18) & (t < 45):
                output = "{0:.3f}\n".format(t)
                pause = False
            else:
                if not pause:
                    output = '\n'
                    pause = True
            
        if not output == '':
            ff.write(output)
            
    ff.write('\n')

f.close()
ff.close()


    
