import velociparser
import time

'''
velociparser.download_main_page()
for url in velociparser.get_scenery_urls():
    print(url)
    velociparser.download_scenery_page(url)
    time.sleep(0.5)
for url in velociparser.get_track_urls():
    print(url)
    velociparser.download_track_page(url)
    time.sleep(0.5)
    
'''

#for f in velociparser.get_track_files_list():
#    print(f)


#result = velociparser.get_track_leaderboard('track_33_267.html')

#js = json.dumps(result, sort_keys=True, indent=2)
#f = open('dump.json', 'w')
#f.write(js)
#f.close()



'''
# download all
if False:
    scenery_urls = get_scenery_urls(version = 14)
    for sc_url in scenery_urls:
        track_urls = get_track_urls(sc_url)
        for tr_url in track_urls:
            download_track_table(tr_url)
            print(tr_url)
            time.sleep(0.5)

# parse downloaded
if False:
    result = {}
    for f in get_track_files():
        p = parse_leaderboard(f)
        if not p['scenery'] in result.keys():
            result[p['scenery']] = {}
        result[p['scenery']][p['track']] = p['leaderboard']
    js = json.dumps(result, sort_keys=True, indent=2)
    f = open('dump.json','w')
    f.write(js)
    f.close()

# process dump
if True:
    with open('dump.json') as f:
        js = json.load(f)

    russian_pilots = set([])
    for scenery in js:
        for track in js[scenery]:
            for entry in js[scenery][track]:
                if entry['country'] == 'Russian Federation':
                    russian_pilots.add(entry['name'])
                if entry['name'] == 'AlexeyStn':
                    print(' %-20s%-30s%8s'%(scenery, track, entry['time']))
'''



