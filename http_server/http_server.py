from http.server import BaseHTTPRequestHandler, HTTPServer

def get_update(n):
    r = []
    something_to_update = 0
    f = open('list.txt')
    for i, line in enumerate(f):
        if i >= n:
            r.append(line[:-1])
            something_to_update = 1
    if not 'i' in locals():
        r = ['0']
    else:
        r.append(str(i+1))
    s = ",".join(r)
    print(s)
    return(s)

def file2bytes(filename):
    f = open(filename)
    s = f.read()
    f.close()
    return bytes(s, 'utf-8')

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        print('path: ' + self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if self.path == '/':
            self.wfile.write(file2bytes('main.html'))       
        elif self.path.startswith('/updates'):
            n = int(self.path.split(sep='=')[1])
            self.wfile.write(bytes(get_update(n), 'utf-8'))
        else:
            self.wfile.write(bytes('file not found', 'utf-8'))           
        


server = HTTPServer(('localhost', 88), Server)
print('Server Starts')

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass

server.server_close()
print('Server Stops')
