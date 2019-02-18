from PIL import Image
from os import listdir

path_in = './input/'
path_out = './output/'



lst = listdir(path_in)

for filename in lst:
    if filename.endswith('.jpeg'):
        im = Image.open(path_in + filename)
        #im = im.resize((1600, 1200), Image.ANTIALIAS)
        #im = im.rotate(270, expand = True)
        im.save(path_out + filename, format='JPEG', quality=65)
        print(filename)





