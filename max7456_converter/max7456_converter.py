from PIL import Image

mcm_name = 'mwosd_default.mcm'
bmp_name = '4.bmp'
bmp_name = mcm_name[:-4] + '.bmp'

font2image = 1 # 0 - image2font, 1 - font2image

if (font2image):
    img = Image.new('L', (16*(12+1) + 1, 16*(18+1) + 1), 64)
    font = open(mcm_name)
    font.readline() # header
else:
    img = Image.open(bmp_name)
    font = open(mcm_name,'w')
    font.write('MAX7456\n')
for cx in range(16):
    for cy in range(16):
        for y in range(18):
            for x in range(3):
                if (font2image):
                    line = font.readline()
                    # print('--' +line)
                else:
                    line = ""
                for i in range(4):
                    coord = ( (12 + 1)*cy + 4*x + i + 1, (18 + 1)*cx + y + 1 )
                    if (font2image):
                        if (line[i*2] == '1'):
                            img.putpixel(coord, 255)
                        elif (line[i*2+1] == '1'):
                            img.putpixel(coord, 128)
                        else:
                            img.putpixel(coord,0)
                    else:
                        p = img.getpixel(coord)
                        if (p == 255):
                            line = line + '10'
                        elif (p == 0):
                            line = line + '00'
                        else:
                            line = line + '01'
                if (font2image == 0):
                    font.write(line + '\n')
        for i in range(10):        
            if (font2image): 
                font.readline()
            else:
                font.write('01010101\n')
if (font2image):    
    img.save(bmp_name)



img.close()
font.close()

if (font2image):
    print(mcm_name + '  -> ' + bmp_name);
else:
    print(bmp_name + '  ->  ' + mcm_name);
    
print('Done')

