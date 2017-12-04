from html.parser import HTMLParser

# first name
# second name
# name
# join date
# post cound
# id

s_list = []

out = open('users.csv', 'wb')
sep = '\t'

class MyHTMLParser(HTMLParser):

    first_name_found = 0
    second_name_found = 0
    join_date_found = 0
    post_count_found = 0
    user_name_found = 0
    id_number = 0
    not_printed = 0
    s = ''
    
    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.s = ''
        if tag == "td":
            for attr in attrs:
                if attr[1] == "alt2":
                    self.first_name_found = 1
                if attr[1] == "alt1":
                    self.second_name_found = 1
                if attr[1] == "alt1 joindate":
                    self.join_date_found = 1
                if attr[1] == "alt1 postcount":
                    self.post_count_found = 1
                if attr[1] == "alt1 username":
                    self.user_name_found = 1
                    self.not_printed = 1
        if tag == "a":
            if self.user_name_found:
                id_number = attrs[1][1][13:]

    def handle_endtag(self, tag):
        global out
        global s_list
        if tag == "tr":
            if self.not_printed:
                self.not_printed = 0
                # print(self.s)
                # ss = self.s.encode('ascii', 'replace')
                # ss = str(ss)

                bytes_string = self.s.encode('cp1251', errors = 'ignore')
                self.s = str(bytes_string,'cp1251')
                
                out.write(self.s)
                s_list.append(self.s)
                out.write('\n')

    def handle_data(self, data):
        global sep
        if self.first_name_found:
            self.s += data + sep
            self.first_name_found = 0
        if self.second_name_found:
            self.s += data + sep
            self.second_name_found = 0
        if self.join_date_found:
            self.s += data + sep
            self.join_date_found = 0
        if self.post_count_found:
            self.s += data + sep
            self.post_count_found = 0
        if self.user_name_found:
            self.s += data + sep
            self.user_name_found = 0
    
parser = MyHTMLParser()

out = open('users.csv', 'w', encoding="cp1251")

for i in range(1,479):
    if i % 10 == 0:
        print(i)
    path = './users/users%03d.html' % i
    f = open(path, 'r', encoding="utf8")
    for s in f:
        parser.feed(s)

f.close()
out.close()

ch = s_list[0][4]; print(ord(ch))


print('Done')
