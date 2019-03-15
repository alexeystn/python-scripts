import os
import time
import json
import requests
import threading
from html.parser import HTMLParser

modes = ['lap1', 'lap3']
mutex = threading.Lock()
download_counter = 0
download_counter_max = 0


def download_main_page():
    r = requests.get('http://www.velocidrone.com')
    with open('./html/main.html', 'wb') as f:
        f.write(r.text.encode('utf-8'))


# Scenery URLs are stored in main page in following format:
# <a href="http://www.velocidrone.com/leaderboard_by_version/XX/1.YY">

def get_scenery_urls():
    version = 14
    url_list = []
    substring = 'https://www.velocidrone.com/leaderboard_by_version'
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
    substring = 'https://www.velocidrone.com/leaderboard/'
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

def download_track_pages_thread(urls, thread_num, mode):
    global download_counter
    global download_counter_max
    s = requests.session()
    if mode == 'lap1':
        s.get('https://www.velocidrone.com/set_race_mode/3')
    elif mode == 'lap3':
        s.get('https://www.velocidrone.com/set_race_mode/6')
    else:
        print('Unknown mode')
        return
    for i, url in enumerate(urls):
        mutex.acquire()
        download_counter += 1
        print('{0}/{1} {2}'.format(download_counter, download_counter_max, url))
        mutex.release()
        r = s.get(url)
        while len(r.text) < 10e3:  # retry if answer is too low
            time.sleep(1)
            r = s.get(url)
            print('Retry: %s' % url)  # tod3o:
        track_id = url.split(sep='/')[-3:-1]
        with open('html/track_' + track_id[0] + '_' + track_id[1] + '_' + mode + '.html', 'wb') as f:
            f.write(r.text.encode('utf-8'))
        time.sleep(0.1)
    s.close()


# Divide URLs list in N parts and download them in parallel threads

def download_track_pages(urls, mode):
    global download_counter
    global download_counter_max
    download_counter = 0
    download_counter_max = len(urls)
    number_of_threads = 4  # 4 is optimum
    number_of_urls_per_thread = len(urls) // number_of_threads
    if len(urls) % number_of_threads:
        number_of_urls_per_thread += 1
    urls_grouped = [[] for i in range(number_of_threads)]
    for i, url in enumerate(urls):
        urls_grouped[int(i // number_of_urls_per_thread)].append(urls[i])
    threads = [threading.Thread(target=download_track_pages_thread, args=(urls_grouped[i], i, mode)) for i in range(number_of_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


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


def download_all_leaderboards(refresh_tracks=False):
    time_start = time.time()
    if refresh_tracks:
        download_main_page()
        scenery_urls = get_scenery_urls()
        download_scenery_pages(scenery_urls)
    track_urls = get_track_urls()
    for m in modes:
        download_track_pages(track_urls, m)
    time_stop = time.time()
    print('Leaderboard downloaded in %.1f sec' % (time_stop - time_start))


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


def date_hash(date_string):
    date = [int(d) for d in date_string.split(sep='/')]
    return date[0] + date[1]*31 * date[2]*31*12
