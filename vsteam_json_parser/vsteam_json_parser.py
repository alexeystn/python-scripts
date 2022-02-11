import json
import time

id_2_nick = {}
with open('./db/sportsman.db', 'r', encoding="utf8") as f:
    for line in f:
        j = json.loads(line)
        if 'nick' in j.keys():
            if len(j['nick']) > 0:
                id_2_nick[j['_id']] = j['nick']

for id_ in id_2_nick:
    print(id_, id_2_nick[id_])

results = {}

with open('./db/lap.db', 'r') as f:
    for line in f:
        j = json.loads(line)
        if 'sportsmanId' in j.keys():
            if j['sportsmanId'] in id_2_nick.keys():
                nick = id_2_nick[j['sportsmanId']]
                if not nick in results.keys():
                    results[nick] = [] 
                if 'timeLap' in j.keys():
                    if j['typeLap'] == 'OK':
                        lap_time = j['timeLap']/1000
                        t = j['millisecond']//1000
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S',
                                                  time.localtime(t))
                        entry = {'Lap': lap_time, 'Time': timestamp}
                        results[nick].append(entry)

with open('output.txt', 'w', encoding="utf8") as f:
    f.write(json.dumps(results, sort_keys=True, indent=2, ensure_ascii=False))

with open('output.csv', 'w', encoding="utf8") as f:
    for pilot in results:
        for entry in results[pilot]:
            line = '{0},{1},{2:.3f}\n'.format(pilot,
                                              entry['Time'],
                                              entry['Lap'])
            f.write(line)





    
