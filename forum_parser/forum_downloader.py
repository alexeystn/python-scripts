import requests
import time

def save_response_to_file(r, filename):
    with open(filename, 'wb') as output_file:
        output_file.write(r.text.encode('utf-8'))

f = open('params.txt')

url_main = f.readline()[:-1]
url_users = f.readline()[:-1]

form_data = {}
form_data['vb_login_username'] = f.readline()[:-1] 
form_data['vb_login_password'] = f.readline()[:-1] 
form_data['do'] = 'login'

s = requests.Session()
r = s.post(url_main, data = form_data)
save_response_to_file(r, 'login.html')
time.sleep(1)
r = s.get(url_main)
save_response_to_file(r, 'main.html')


for i in range (1,1000):
    time.sleep(1)
    r = s.get(url_users + str(i))
    path = './users/users%03d.html' % i
    save_response_to_file(r, path )
    print(i)


print('Done')



