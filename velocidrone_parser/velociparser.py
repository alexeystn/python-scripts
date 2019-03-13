import os
import time
import json
import requests
from html.parser import HTMLParser

modes = ['lap1', 'lap3']


def download_main_page():
    r = requests.get('http://www.velocidrone.com')
    with open('./html/main.html', 'wb') as f:
        f.write(r.text.encode('utf-8'))


# Scenery URLs are stored in main page in following format:
# <a href="http://www.velocidrone.com/leaderboard_by_version/XX/1.YY">

def get_scenery_urls():
    version = 14
    url_list = []
    substring = 'http://www.velocidrone.com/leaderboard_by_version'
    with open('./html/main.html') as f:
        for line in f:
            index_start = line.find(substring)
            if index_start != -1:
                index_stop = line.find('"', index_start)
                url = line[index_start:index_stop]
                if url.endswith(str(version)):
                    url_list.append(url)
    return url_list


def download_scenery_pages(urls):
    for i, url in enumerate(urls):
        print('{0}/{1} {2}'.format(i + 1, len(urls), url))
        scenery_id = url.split(sep='/')[-2]
        r = requests.get(url)
        with open('html/scenery_' + scenery_id + '.html', 'wb') as f:
            f.write(r.text.encode('utf-8'))
        time.sleep(0.1)


# Track leaderboards are stored in scenery pages in following format:
# <a href="http://www.velocidrone.com/leaderboard/XX/YYY/Z.ZZ">

def get_track_urls():
    url_list = []
    substring = 'http://www.velocidrone.com/leaderboard/'
    scenery_file_list = [f for f in os.listdir('./html') if f.startswith('scenery')]
    for scenery_file in scenery_file_list:
        with open('./html/' + scenery_file) as f:
            for line in f:
                index_start = line.find(substring)
                if index_start != -1:
                    index_stop = line.find('"', index_start)
                    url = line[index_start:index_stop]
                    url_list.append(url)
    return url_list


# In order to choose 'Single' of '3 Lap' mode 'set_race_mode' request
# should be sent to server in current session

def download_track_pages(urls, mode):
    s = requests.session()
    if mode == 'lap1':
        s.get('https://www.velocidrone.com/set_race_mode/3')
    elif mode == 'lap3':
        s.get('https://www.velocidrone.com/set_race_mode/6')
    else:
        print('Unknown mode')
        return
    for i, url in enumerate(urls):
        print('{0}/{1} {2}'.format(i + 1, len(urls), url))
        track_id = url.split(sep='/')[-3:-1]
        r = s.get(url)
        with open('html/track_' + track_id[0] + '_' + track_id[1] + '_' + mode + '.html', 'wb') as f:
            f.write(r.text.encode('utf-8'))
        time.sleep(0.1)
    s.close()


def get_track_files_list(mode):
    result = []
    for filename in os.listdir('html'):
        if filename.startswith('track_') and (mode in filename):
            result.append(filename)
    return result


# Best times are located in table rows enclosed in <tr><td> tags in following format:
#   Pos | Time | Name | Country | Rank | Model | Date | Version

class MyHTMLParser(HTMLParser):

    leaderboard = []
    entry = []
    cell_content = ''

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.entry = []
        if tag == "td":
            self.cell_content = ''

    def handle_endtag(self, tag):
        if tag == "tr":
            if self.entry:
                e = self.entry
                e[2] = e[2].replace('(', ' (')
                self.leaderboard.append({'name': e[2], 'country': e[3], 'time': e[1], 'position': e[0], 'date': e[6]})
            self.entry = []
        if tag == "td":
            self.entry.append(self.cell_content)

    def handle_data(self, data):
        self.cell_content += data.strip()


# Track name is located between <h3 class=""> and <span class="small_link"> tags
# Location name is enclosed by <h2></h2>

def get_track_leaderboard(filename):
    result = {}
    parser = MyHTMLParser()
    parser.leaderboard = []
    head_scenery_name = '<h2>'
    tail_scenery_name = '</h2>'
    head_track_name = '<h3 class="">'
    tail_track_name = '<span'
    with open('html/' + filename) as f:
        for string in f:
            start_ind = string.find(head_scenery_name)
            if start_ind != -1:
                start_ind += len(head_scenery_name)
                stop_ind = string.find(tail_scenery_name)
                result['scenery'] = string[start_ind:stop_ind].strip()
            start_ind = string.find(head_track_name)
            if start_ind != -1:
                start_ind += len(head_track_name)
                stop_ind = string.find(tail_track_name)
                result['track'] = string[start_ind:stop_ind].strip()
            parser.feed(string)
    result['leaderboard'] = parser.leaderboard
    return result


def download_all_leaderboards():
    download_main_page()
    scenery_urls = get_scenery_urls()
    download_scenery_pages(scenery_urls)
    track_urls = get_track_urls()
    for m in modes:
        download_track_pages(track_urls, m)


def parse_all_leaderboards_to_json():
    for m in modes:
        result = {}
        track_files_list = get_track_files_list(m)
        for i, track in enumerate(track_files_list):
            print('{0}/{1} {2}'.format(i + 1, len(track_files_list), track))
            p = get_track_leaderboard(track)
            if not p['scenery'] in result.keys():
                result[p['scenery']] = {}
            result[p['scenery']][p['track']] = p['leaderboard']
        js = json.dumps(result, sort_keys=True, indent=2)
        with open('dump_' + m + '.json','w') as f:
            f.write(js)


def load_leaderboards_from_json():
    js = {}
    for m in modes:
        with open('dump_' + m + '.json') as f:
            js[m] = json.load(f)
    return js
