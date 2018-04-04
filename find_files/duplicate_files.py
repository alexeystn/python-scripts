import os

##original_path = '/Users/imac/Pictures/LG V10 backup'
##originals = os.listdir(original_path)
##originals.remove('.DS_Store')
##
##for root, dirs, files in os.walk('/Users/imac/Pictures'):
##    for file in files:
##        if file in originals:
##            if root != original_path:
##                print(root+'\\'+file)

cnt = 0

images = []
paths = []

for root, dirs, files in os.walk('/Users/imac/Pictures'):
    for file in files:
        if (file != '.DS_Store') & (not 'aplibrary' in root) & (not 'WhatsApp' in root):
            images += [file]
            paths += [root]

full = list(zip(images, paths))
full.sort()

for i in range(len(full)-1):
    if full[i][0] == full[i+1][0]:
        print(full[i][1] + '\\' + full[i][0])
        print('= '+full[i+1][1] + '\\' + full[i+1][0])

