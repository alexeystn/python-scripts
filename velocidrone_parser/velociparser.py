import os
import time
import json
import requests
from html.parser import HTMLParser


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


def download_scenery_page(scenery_url):
    scenery_id = scenery_url.split(sep='/')[-2]
    r = requests.get(scenery_url)
    with open('html/scenery_' + scenery_id + '.html', 'wb') as f:
        f.write(r.text.encode('utf-8'))


# Track leaderboards are stored in scenery pages in following format:
# <a href="http://www.velocidrone.com/leaderboard/XX/YYY/1.ZZ">

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


def download_track_page(track_url):
    track_id = track_url.split(sep='/')[-3:-1]
    r = requests.get(track_url)
    with open('html/track_' + track_id[0] + '_' + track_id[1] + '.html', 'wb') as f:
        f.write(r.text.encode('utf-8'))


def get_track_files_list():
    result = []
    for filename in os.listdir('html'):
        if filename.startswith('track_'):
            result.append(filename)
    return result


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
    for i, url in enumerate(scenery_urls):
        print('{0}/{1} {2}'.format(i + 1, len(scenery_urls), url))
        download_scenery_page(url)
        time.sleep(0.1)
    track_urls = get_track_urls()
    for i, url in enumerate(track_urls):
        print('{0}/{1} {2}'.format(i + 1, len(track_urls), url))
        download_track_page(url)
        time.sleep(0.1)


def parse_all_leaderboards_to_json():
    result = {}
    track_files_list = get_track_files_list()
    for i, track in enumerate(track_files_list):
        print('{0}/{1} {2}'.format(i + 1, len(track_files_list), track))
        p = get_track_leaderboard(track)
        if not p['scenery'] in result.keys():
            result[p['scenery']] = {}
        result[p['scenery']][p['track']] = p['leaderboard']
    js = json.dumps(result, sort_keys=True, indent=2)
    with open('dump.json','w') as f:
        f.write(js)


def load_leaderboard_from_json():
    with open('dump.json') as f:
        js = json.load(f)
    return js
