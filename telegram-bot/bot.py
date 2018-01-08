import requests
from io import BytesIO
import json
from urllib.parse import quote
from time import sleep



f = open('token.txt')
token = f.readline()[:-1]
url_base = 'https://api.telegram.org/bot' + token

while True:

    url = url_base + '/getUpdates'
    response = requests.get(url)
    j = json.load(BytesIO(response.content))

    update_id = 0
    for result in j['result']:
        if result['update_id'] > update_id:
            update_id = result['update_id']
        client_id = result['message']['from']['id']
        client_name = result['message']['from']['username']
        client_text = result['message']['text']
        text = 'from ' + client_name + ' received: ' + quote(client_text)
        print(text) 
        text = 'from ' + client_name + ' received: ' + client_text
        url = url_base + '/sendMessage'
        url += '?chat_id=' + str(client_id)
        url += '&text=' + quote(text)
        requests.get(url)
    sleep(0.25)
    print('.')
        
    url = url_base + '/getUpdates?offset=' + str(update_id + 1) 
    response = requests.get(url)


print('Done')

