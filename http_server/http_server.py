from http.server import BaseHTTPRequestHandler, HTTPServer
from random import random
from time import time

names = ['Alexey', 'Andrew']
previous_time = time()
laps = []

def generate_event():
    global previous_time
    current_time = time()
    lap_time = current_time - previous_time
    previous_time = current_time
    lap_time_str = '{0:.3f}'.format(lap_time)
    laps.append(lap_time_str)
    print(lap_time_str)
    if lap_time < 1.5:
        return 1
    else:
        return 0

def get_updates(n):
    s = str(len(laps))
    if n < len(laps):
        for i in range(n,len(laps)):
            s += ',' + laps[i]
    print(s)
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
            s = names[0] + ',' + names[1]
            s = 'sensor2=ir,name1=hey'
            response = bytes(s, 'utf-8')
        elif request.startswith('/save'):
            s = request.split(sep='=')[1].split(sep=',')
            names = s;
            response = text2bytes('confirm.html')
        elif request == '/status':
            response = bytes(str(random()), 'utf-8')
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
