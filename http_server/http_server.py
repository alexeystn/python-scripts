from http.server import BaseHTTPRequestHandler, HTTPServer
from random import random
from time import time

names = ['Alexey', 'Andrew']
previous_time = time()
events = []

pilots_num = 2
pilots = [{} for i in range(pilots_num)]


pilots[0]['en'] = 1
pilots[0]['name'] = 'Alexey'
pilots[0]['sens'] = 'vtx'
pilots[0]['ch'] = 2
pilots[0]['id'] = 22
pilots[0]['thr'] = 222

pilots[1]['en'] = 1
pilots[1]['name'] = 'Andrew'
pilots[1]['sens'] = 'ir'
pilots[1]['ch'] = 5
pilots[1]['id'] = 55
pilots[1]['thr'] = 555


def save_settings(s):
    global pilots
    s = s.split(sep='?')[1]
    for p in s.split(sep='&'):
        n = int(p[5]) - 1;
        for f in p.split(sep=',')[1:]:
            par = f.split(sep='=')
            pilots[n][par[0]] = par[1]
    print(pilots)

def load_settings():
    global pilots
    s = ['' for i in range(len(pilots))]

    for i, pilot in enumerate(pilots):
        s[i] = 'pilot' + str(i+1)
        for k in pilots[i].keys():
            s[i] += ',' + k + '=' + str(pilots[i][k])
    s = '&'.join(s)
    print(s)
    return bytes(s, 'utf-8')


def generate_event():
    global previous_time
    current_time = time()
    lap_time = current_time - previous_time
    previous_time = current_time
    ev_time = '{0:.3f}'.format(lap_time)
    ev_pilot_num = str(round(random()))
    ev_type = str(round(random()))
    event_str = ev_pilot_num + '-' + ev_type + '-' + ev_time
    events.append(event_str)
    print('event: ' + event_str)
    if lap_time < 1.5:
        return 1
    else:
        return 0

def random_status():
    s = '{0:.1f},{1:.0f}'.format(random()*2.6+10, random()*4096)
    return bytes(s, 'utf-8')

def get_updates(n):
    s = str(len(events))
    if n < len(events):
        for i in range(n,len(events)):
            s += ',' + events[i]
    print('updates: ' + s)
    return bytes(s, 'utf-8')


def text2bytes(filename):
    f = open(filename)
    s = f.read()
    f.close()
    return bytes(s, 'utf-8')

def image2bytes(filename):
    f = open(filename, 'rb')
    s = f.read()
    f.close()
    return s

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        global names
        print('path: ' + self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        request = self.path

        if request == '/':
            response = text2bytes('main.html')
        elif request == '/favicon.ico':
            response = image2bytes('favicon.png')
        elif request == '/setup':
            response = text2bytes('setup.html')
        elif request == '/styles.css':
            response = text2bytes('styles.css')
        elif request == '/load':
            response = load_settings()
        elif request.startswith('/save'):
            save_settings(request)
            response = text2bytes('confirm.html')
        elif request == '/status':
            response = random_status()
        elif request.startswith('/update'):
            n = int(request.split(sep='=')[1])
            response = get_updates(n)
        else:
            response = bytes("Error 404. Page not found.", 'utf-8')

            
        self.wfile.write(response)

    

server = HTTPServer(('192.168.1.4', 8888), Server)
print('Server Starts')

while True:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        r = generate_event()
        if r:
            break
        pass

server.server_close()
print('Server Stops')
