import os

def get_image_type(name):
    if name[4] == name[7] == '-':
        return 'db'
    elif name[8] == '_':
        return 'cam'
    else:
        return 'unknown'

def transform_cam_db(name):
    date = [name[0:4], name[4:6], name[6:8]]
    time = [name[9:11], name[11:13], name[13:15]]
    ext = name.split('.')[-1]
    return '-'.join(date) + ' ' + '.'.join(time) + '.' + ext

def transform_db_cam(name):
    date = name[0:10].split(sep='-')
    time = name[11:19].split(sep='.')
    name.split('.')[-1]
    return ''.join(date) + '_' + ''.join(time) + '.' + ext

path = '/Users/imac/Desktop/Korea'
files = os.listdir(path)

for filename in files:
    image_type = get_image_type(filename)
    if image_type == 'db':
        new_filename = transform_db_cam(filename)
    elif image_type == 'cam':
        new_filename = transform_cam_db(filename)
    else:
        new_filename = None

    if new_filename:
        print(filename + ' -> ' + new_filename)
        os.rename(os.path.join(path, filename), os.path.join(path, new_filename))
    
