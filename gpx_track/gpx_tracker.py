import xml.etree.ElementTree as ET
#import matplotlib.pyplot as plt


filename = 'tr.gpx'

tree = ET.parse(filename)
root = tree.getroot()

tracks = []
empty_track = {'lat':[], 'lon':[], 'ele':[], 'time':[]}

for trk in root:
    if 'trk' in trk.tag:
        print('Track found')
        for trkseg in trk:
            if 'trkseg' in trkseg.tag:
                tracks.append(empty_track)
                print('Track segment found')
                for trkpt in trkseg:
                    if 'trkpt' in trkpt.tag:
                        # point found
                        s = {}
                        for p in trkpt:
                            if 'time' in p.tag:
                                s['time'] = p.text
                            if 'ele' in p.tag:
                                s['ele'] = float(p.text)
                        if len(s.items()) == 2:
                            tracks[-1]['lat'].append(float(trkpt.attrib['lat']))
                            tracks[-1]['lon'].append(float(trkpt.attrib['lon']))
                            tracks[-1]['ele'].append(s['ele'])
                            tracks[-1]['time'].append(s['time'])
i = 1
                            
#plt.plot(tracks[i]['lon'], tracks[i]['lat'])
#plt.show()
