import velociparser

# velociparser.download_all_leaderboards()
# velociparser.parse_all_leaderboards_to_json()

js = velociparser.load_leaderboard_from_json()

russian_pilots = set()
countries = {}

for scenery in js:
    for track in js[scenery]:
        for entry in js[scenery][track]:

            if not entry['country'] in countries.keys():
                countries[entry['country']] = set()
            countries[entry['country']].add(entry['name'])

            if entry['name'] == 'Eugy01':
                print(' %-20s%-27s%8s%6s/%-2s%14s'%(scenery, track, entry['time'], entry['position'],
                   len(js[scenery][track]), entry['date']))

country_list = list(countries.keys())
country_list.sort(key=lambda cnt: len(countries[cnt]), reverse=True)

# for country in country_list:
#     print('%20s: %d' % (country, len(countries[country])))
