import os
import re
import json
import requests
from datetime import datetime


def load_project_list():
    with open('projects.json', 'r') as f:
        data = json.load(f)
        print('Loaded projects:')
        print(data)
    return list(data.keys())


def download_id_price_pairs(project, archive_enabled=False):

    url = 'https://api-selectel.pik-service.ru/v2/filter'
    params = {'block': project['id'],
              'areaFrom': 35,
              'flatPage': 1,
              'flatLimit': 50,
              'onlyFlats': 1,
              'sortBy': 'price'}
    url += '?' + '&'.join(k + '=' + str(params[k]) for k in params)
    response = requests.get(url)

    print(project['name'])
    id_price_pairs = []
    for flat in json.loads(response.content)['blocks'][0]['flats']:
        print(flat['id'], flat['price'])
        id_price_pairs.append((flat['id'], flat['price']))

    if archive_enabled:
        filename = './archive/'
        filename += datetime.now().strftime('%Y%m%d_%H%M%S')
        filename += '_' + project['url'] + '.json'
        with open(filename, 'wb') as f:
            f.write(response.content)

    return id_price_pairs


def download_project_list():

    url = 'https://api.pik.ru/v2/filter?sort=blocks&onlyBlocks=1'
    response = requests.get(url)

    project_list = []
    for project in json.loads(response.content):
        project_list.append({'id': project['id'],
                             'name': project['name'],
                             'url': project['url']})
    return project_list


class Parser:

    filename = 'temp.html'

    def download_html(self, project):
        url = 'https://old.pik.ru/search/{0}'.format(project) +\
              '?rooms=1,2&areaFrom=35&sortBy=price'
        command = 'curl "{0}" -o {1} -k'.format(url, self.filename)
        print(command)
        os.system(command)

    def get_id_price_pairs(self, filename=None):
        if not filename:
            filename = self.filename
        with open(filename, 'r', encoding="utf-8") as f:
            for line in f:
                if len(line) > 1e6:
                    break

        id_price_pairs = []

        p_price = re.compile(r'от \d{1,2} \d{3} \d{3}')
        p_id = re.compile(r'data-id="\d{6}"')

        for m_id, m_price in zip(p_id.finditer(line), p_price.finditer(line)):
            int_id = int(m_id.group()[9:-1])
            int_price = int(''.join((m_price.group()[3:].split())))
            id_price_pairs.append((int_id, int_price))
            print(int_id, int_price)

        return id_price_pairs

    def put_to_archive(self, project):
        new_filename = './archive/'
        new_filename += datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename += '_' + project + '.html'
        os.rename(self.filename, new_filename)
