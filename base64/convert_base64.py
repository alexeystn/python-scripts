import base64

bin_file = 'ticket.pdf'
txt_file = 'input.log'

f_in = open(txt_file, 'rb')
f_out = open(bin_file, 'wb')
f_out.write(base64.b64decode(f_in.read()))
f_in.close()
f_out.close()


