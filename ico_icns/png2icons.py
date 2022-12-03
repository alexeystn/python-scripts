from PIL import Image
import os

filename_png = 'tiny_bb.png'
output_path = '../../tiny-blackbox/Software/resources/'

filename = filename_png.split(sep='.')[0]

sizes = [16, 32, 128, 256, 512]
image = Image.open(filename_png)


if 1:  # macOS
    output_dir = filename + '.iconset'
    if not (os.path.isdir(output_dir)):
        os.mkdir(output_dir)
    for sz in sizes:
        image1 = image.resize((sz, sz))
        image1.save(os.path.join(output_dir, 'icon_{0}x{0}.png'.format(sz)))
        image2 = image.resize((sz*2, sz*2))
        image2.save(os.path.join(output_dir, 'icon_{0}x{0}@2x.png'.format(sz)))
    os.system('iconutil --convert icns --output {0}.icns {1}'.format(filename, output_dir))

if 1:  # Windows ico
    image.save(filename + '.ico', sizes=[(a, a) for a in sizes])

if 1:  # remove temp files:
    for f in os.listdir(filename + '.iconset'):
        os.remove(filename + '.iconset/' + f)
    os.rmdir(filename + '.iconset')

if 1:  # move to output directory
    for ext in ['.ico', '.icns']:
        os.rename(filename + ext, output_path + filename + ext)
