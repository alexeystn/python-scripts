import os

path = '/Users/imac/Desktop/20200629_Photo'


def get_size(start_path = '.'):
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def get_size_mb(path):
    
    size = get_size(path)
    size = size/2**20
    return int(size)


folder_dict = dict()

folder_list = os.listdir(path)


for f in folder_list:
    dir_path = os.path.join(path, f)
    dir_name = f
    dir_size = int(get_size(dir_path)/2**20)
    s = '{0:5} Mb - {1}'.format( dir_size, dir_name)
    if (dir_size > 10):
        print(s)





#print(get_size(), 'bytes')


