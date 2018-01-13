import requests
from io import BytesIO
from PIL import Image
import socket
import time
import json

conf = { 'url': 'http://192.168.42.1/DCIM/100MEDIA/',
         'ip-address': '192.168.42.1',
         'tcp-port': 7878,
         'buf-size': 1024 }
         
def xiaomi_yi_make_photo():
    global conf
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((conf['ip-address'], conf['tcp-port']))
    j = {'msg_id': 257, 'token': 0, 'param': 0}
    message = json.dumps(j)
    s.send(message.encode())    
    data = s.recv(conf['buf-size'])
    data = s.recv(conf['buf-size'])
    j = json.loads(data.decode())
    token = j['param']
    print('Connected with token {:d}'.format(token))
    j = {'msg_id': 769, 'token': token}
    message = json.dumps(j)
    s.send(message.encode())
    print('Making photo...')
    time.sleep(1)
    s.close()
    time.sleep(1)
    print('Done')         

def get_images_filenames(s):
    substring = 'href="YDXJ'
    indexes = []
    photo_numbers = []
    ex = 0
    while ex != -1:
        ex = s.find(substring, ex+10)
        indexes.append(ex)
    indexes.remove(-1)
    for i in indexes:
        n = int(s[i+10:i+14])  
        photo_numbers.append(n)
    return photo_numbers

def xiaomi_yi_download_latest_file():
    response = requests.get(conf['url'])
    photo_numbers = get_images_filenames(response.text)
    print('Photos in memory:')
    print(photo_numbers)
    latest_photo = photo_numbers[-1:][0]
    print('Downloading photo...')
    response = requests.get(conf['url'] + 'YDXJ{:04d}.jpg'.format(latest_photo))
    im = Image.open(BytesIO(response.content))
    im.save('YDXJ{:04d}.jpg'.format(latest_photo))
    print('Done')


xiaomi_yi_make_photo()
xiaomi_yi_download_latest_file()



