import velociparser

# velociparser.download_all_leaderboards(refresh_tracks=False, override_version=10)
# velociparser.parse_all_leaderboards_to_json()

# js = velociparser.load_leaderboards_from_json()
js_full = velociparser.load_leaderboards_from_json_by_versions([11, 12, 13, 14])

pilots_by_countries = {}
tracks_by_pilots = {}
tracks_popularity = {}

for j in js_full:
    js = js_full[j]
    for mode in js:
        for scenery in js[mode]:
            for track in js[mode][scenery]:

                full_track_name = scenery + ' - ' + track
                if not full_track_name in tracks_popularity:
                    tracks_popularity[full_track_name] = dict.fromkeys(js.keys(), 0)

                for entry in js[mode][scenery][track]:

                    tracks_popularity[full_track_name][mode] += 1

                    if not entry['country'] in pilots_by_countries:
                        pilots_by_countries[entry['country']] = set()
                    pilots_by_countries[entry['country']].add(entry['name'])

                    if not entry['name'] in tracks_by_pilots:
                        tracks_by_pilots[entry['name']] = {'country': entry['country'], 'results': [], 'latest': '0/0/0'}
                    tracks_by_pilots[entry['name']]['results'].append(
                        {'track': full_track_name, 'mode': mode, 'time': entry['time'], 'date': entry['date'],
                         'position': entry['position'] + '/' + str(len(js[mode][scenery][track]))}
                    )
                    if velociparser.date_hash(entry['date']) > velociparser.date_hash(tracks_by_pilots[entry['name']]['latest']):
                        tracks_by_pilots[entry['name']]['latest'] = entry['date']


# Track leaderboard
if 0:
    scenery = 'Football Stadium'
    track = 'Split-S'
    mode = 'lap1'
    leaderboard = js[mode][scenery][track]
    for entry in leaderboard:
        print('%6s%10s   %-20s%-20s' % (entry['position'], entry['time'], entry['name'], entry['country']))

# Pilot personal results
if 0:
    name = 'AlexeyStn'
    for mode in js:
        print(mode[-1] + ' laps:')
        for tr in tracks_by_pilots[name]['results']:
            if tr['mode'] == mode:
                print('%50s%10s%10s%14s' % (tr['track'], tr['time'], tr['position'], tr['date']))
    print('Latest: ' + tracks_by_pilots[name]['latest'])

# Most popular tracks
if 0:
    mode = 'lap1'
    track_list = list(tracks_popularity)
    track_list.sort(key=lambda tr: tracks_popularity[tr][mode], reverse=True)
    for tr in track_list[:10]:
        print('%5d - %s' % (tracks_popularity[tr][mode], tr))

# Most active pilots
if 0:
    pilots_list = list(tracks_by_pilots)
    pilots_list.sort(key=lambda n: len(tracks_by_pilots[n]['results']), reverse=True)
    for pilot in pilots_list[:30]:
        print('%5d %-20s %-20s' % (len(tracks_by_pilots[pilot]['results']), pilot, tracks_by_pilots[pilot]['country']))

# Number of pilots by countries:
if 0:
    country_list = list(pilots_by_countries)
    country_list.sort(key=lambda c: len(pilots_by_countries[c]), reverse=True)
    total_pilots = 0
    for country in country_list:
        total_pilots += len(pilots_by_countries[country])
        print('%20s: %d' % (country, len(pilots_by_countries[country])))
    print('-' * 30)
    print('%20s: %d' % ('Total', total_pilots))

# Pilots from country:
if 0:
    country = 'Russian Federation'
    pilots = list(pilots_by_countries[country])
    pilots.sort(key=lambda x: x.upper())
    for pilot in pilots:
        print(pilot)
