import requests
from io import BytesIO
import json
from urllib.parse import quote
from urllib.parse import urlencode
from time import sleep
import random

def Telegram_Receive():
    global url_base
    url = url_base + '/getUpdates'
    response = requests.get(url)
    j = json.load(BytesIO(response.content))
    return j

def Telegram_Flush(update_id):
    global url_base
    url = url_base + '/getUpdates?offset=' + str(update_id + 1) 
    response = requests.get(url)

def Telegram_Send(cliend_id, text):
    url = url_base + '/sendMessage?'
    url += urlencode({'chat_id':client_id, 'text': answer_text})    
    requests.get(url)

def Telegram_Debug(result):
    client_id = result['message']['from']['id']
    client_name = result['message']['from']['username']
    client_text = result['message']['text']
    print('from ' + client_name + ' received: ', end='')
    print(quote(client_text))

def Pilot_Lap_String(pilot):
    if pilot == 0:
        s = 'Chip (ch2): '
    else:
        s = 'Dale (ch5): '
    time = 20 + 10*random.random()
    s += '00:{0:.2f}'.format(time)
    return s





subscriber_ids = []
tick_counter = 0
pilot = 0


f = open('token.txt')
token = f.readline()[:-1]
url_base = 'https://api.telegram.org/bot' + token

while True:
    latest_update_id = 0
    j = Telegram_Receive()
    for result in j['result']:
        if result['update_id'] > latest_update_id:
            latest_update_id = result['update_id']
        client_id = result['message']['from']['id']
        client_name = result['message']['from']['username']
        client_text = result['message']['text']

        Telegram_Debug(result)
        if client_text == '/results':
            answer_text = ''
            answer_text += 'Best laps:\n'
            answer_text += Pilot_Lap_String(0) + '\n'
            answer_text += Pilot_Lap_String(1)
            Telegram_Send(client_id, answer_text)

        elif client_text == '/join':
            if client_id in subscriber_ids:
                answer_text = 'You already joined.'
            else:
                subscriber_ids.append(client_id)
                answer_text = 'You joined the race.\nNotifications ON'
            Telegram_Send(client_id, answer_text)

        elif client_text == '/leave': 
            if client_id in subscriber_ids:
                subscriber_ids.remove(client_id)
                answer_text = 'You left the race.\nNotifications OFF'
            else:
                answer_text = 'You already left.'               
            Telegram_Send(client_id, answer_text)
        else:
            answer_text = 'Unknown command'
            Telegram_Send(client_id, answer_text)
        
    sleep(0.25)
    print('.')
    if j['result'] != []:
        Telegram_Flush(latest_update_id)

    tick_counter += 1
    if tick_counter == 4:
        tick_counter = 0
        for sub_id in subscriber_ids:
            answer_text = Pilot_Lap_String(pilot)
            pilot ^= 1
            Telegram_Send(sub_id, answer_text)



