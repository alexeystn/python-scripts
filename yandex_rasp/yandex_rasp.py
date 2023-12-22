import sys
import requests
import numpy as np
import json
from datetime import datetime, timedelta
from transliterate import translit

def load_api_key():
    filename = 'api_key.txt'
    try:
        with open(filename, 'r') as f:
            key = f.readline().strip()
    except FileNotFoundError:
        print('File "{0}" not found. Creating new file.'.format(filename))
        f = open(filename, 'w')
        f.close()
        sys.exit(-1)
    if len(key) == 0:
        print('API key is empty.')
        sys.exit(-1)
    print('API key loaded.')
    return key


def get_schedule(key, date, archive=True):
    station_code = 's9879173'
    url = '&'.join(['https://api.rasp.yandex.net/v3.0/schedule/?apikey={0}'.format(key),
                    'lang=ru_RU', 'station={0}'.format(station_code),
                    'date={0}-{1:02d}-{2:02d}'.format(date.year, date.month, date.day),
                    'transport_types=train'])
    x = requests.get(url)
    response = json.loads(x.content.decode())
    if archive:
        with open('response.json', 'w') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
    return response['schedule']


def format_datetime(d, no_date=False):
    if no_date:
        return d.strftime("%H:%M:%S")
    else:
        return d.strftime("%Y-%m-%d  %H:%M:%S")


north_destinations = ['Санкт-Петербург', 'Мурманск', 'Рыбинск']
delta_time = 15  # minutes between my station ans East Terminal

api_key = load_api_key()

schedule = []
now = datetime.now()

for i in range(1):  # possibly 2 or 3 days

    schedule_day = get_schedule(api_key, now + timedelta(days=i))

    for s in schedule_day:
        uid = s['thread']['uid']
        title = s['thread']['title']
        number = s['thread']['number']
        direction = None

        for destination in north_destinations:
            if title.endswith(destination):
                direction = 'north'
                station_time = datetime.fromisoformat(s['departure'])
                pass_time = station_time + timedelta(minutes=delta_time)
            if title.startswith(destination):
                direction = 'south'
                station_time = datetime.fromisoformat(s['arrival'])
                pass_time = station_time - timedelta(minutes=delta_time)

        if not direction:
            try:
                station_time = datetime.fromisoformat(s['arrival'])  # just to display
            except TypeError:
                station_time = datetime.fromisoformat(s['departure'])
            pass_time = station_time

        entry = {'number': number,
                 'title': title,
                 'direction': direction,
                 'station_time': station_time,
                 'pass_time': pass_time}

        if not entry in schedule:
            schedule.append(entry)

schedule = sorted(schedule, key=lambda d: d['pass_time'])

diff = [abs(datetime.timestamp(now) - datetime.timestamp(s['pass_time'])) for s in schedule]
nearest_idx = diff.index(min(diff))
if min(diff) > delta_time * 60:
    nearest_idx += 1

for i, s in enumerate(schedule):
    line = '{0:8s}{1:38s}'.format(translit(s['number'], 'ru', reversed=True),
                                  translit(s['title'], 'ru', reversed=True))
    if s['direction']:
        line += format_datetime(s['pass_time'])
        if s['direction'] == 'north':
            line += '  <-  '
        else:
            line += '  ->  '
        line += format_datetime(s['station_time'], no_date=True)
    else:
        line += format_datetime(s['station_time'])
        continue
#    if i == nearest_idx:
#        line += '  <<<'

    if datetime.timestamp(s['pass_time']) < datetime.timestamp(now - timedelta(hours=1)):
        continue

    print(line)
