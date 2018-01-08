import requests
from io import BytesIO
import json
from urllib.parse import quote
from urllib.parse import urlencode
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
        print('from ' + client_name + ' received: ', end='')
        print(quote(client_text))
        answer_text = 'You sent: ' + client_text
        if client_text == '/results':
            answer_text = 'Best laps:\nChip: 00:23.12\nDale: 00:24.47'
        url = url_base + '/sendMessage?'
        url += urlencode({'chat_id':client_id, 'text': answer_text})
        requests.get(url)
    sleep(0.25)
    print('.')
        
    url = url_base + '/getUpdates?offset=' + str(update_id + 1) 
    response = requests.get(url)


print('Done')

