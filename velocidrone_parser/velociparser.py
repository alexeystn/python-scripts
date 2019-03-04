import requests
from html.parser import HTMLParser
from os import listdir

def get_scenery_urls(version):
    url_list = []
    r = requests.get('http://www.velocidrone.com')
    f = open('html/main.html', 'wb')
    f.write(r.text.encode('utf-8'))
    f.close()
    substring = 'http://www.velocidrone.com/leaderboard_by_version'
    for string in r.text.splitlines():
        index_start = string.find(substring)
        if index_start != -1:
            index_stop = string.find('"', index_start)
            url = string[index_start:index_stop]
            if url.endswith(str(version)):
                url_list.append(url)
    return url_list

def get_track_urls(scenery_url):
    url_list = []
    r = requests.get(scenery_url)
    f = open('html/scenery_' + scenery_url.split(sep='/')[-2] +'.html', 'wb')
    f.write(r.text.encode('utf-8'))
    f.close()
    substring = 'http://www.velocidrone.com/leaderboard/'
    for string in r.text.splitlines():
        index_start = string.find(substring)
        if index_start != -1:
            index_stop = string.find('"', index_start)
            url = string[index_start:index_stop]
            url_list.append(url)
    return url_list

def download_track_table(track_url):
    r = requests.get(track_url)
    track_url = track_url.split(sep='/')
    f = open('html/track_' + track_url[-3] + '_' + track_url[-2] + '.html', 'wb')
    f.write(r.text.encode('utf-8'))
    f.close()

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
            if self.entry != []:
                e = self.entry[1:4]
                self.leaderboard.append({'name':e[1], 'time':e[0], 'country':e[2]})
            self.entry = []
        if tag == "td":
            self.entry.append(self.cell_content)
    def handle_data(self, data):
        self.cell_content += data.strip()

def parse_leaderboard(filename):
    result = {}
    parser = MyHTMLParser()
    parser.leaderboard = []
    f = open('html/' + filename)
    for string in f:
        start_ind = string.find('<h2>')
        if start_ind != -1:
            start_ind += 4
            stop_ind = string.find('</h2>')
            result['scenery'] = string[start_ind:stop_ind].strip()
        start_ind = string.find('<h3 class="">')
        if start_ind != -1:
            start_ind += 13
            stop_ind = string.find('<span')
            result['track'] = string[start_ind:stop_ind].strip()
        parser.feed(string)
    f.close()
    result['leaderboard'] = parser.leaderboard
    return result

def get_track_files():
    result = []
    for filename in listdir('html'):
        if filename.startswith('track_'):
            result.append(filename)
    return result
    

