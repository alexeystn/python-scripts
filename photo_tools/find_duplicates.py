import os
import hashlib

def get_file_md5(filename):
    with open(filename, 'rb') as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        limit = 100
        while chunk and limit:
            file_hash.update(chunk)
            chunk = f.read(8192)
            limit -= 1
    return file_hash.hexdigest()

def create_md5_dict(path):
    file_list = os.listdir(path)
    checksum_dict = {get_file_md5(os.path.join(path, f)): f for f in file_list}
    return checksum_dict

path_src = '/Users/imac/Desktop/Korea'
dict_src = create_md5_dict(path_src)

path_dst = '/Users/imac/Pictures/2016.03 Korea'
dict_dst = create_md5_dict(path_dst)


for src in dict_src:
    src_name = dict_src[src]
    print(src_name + ' - ', end='')
    if src in dict_dst.keys():
        print(dict_dst[src])
    else:
        print()
        
        





#for d in dict_src:
#    print(d + ': ' + dict_src[d])


