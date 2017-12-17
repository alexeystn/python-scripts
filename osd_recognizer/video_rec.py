from osd_recognizer import OSD_Recognizer
import cv2


r = OSD_Recognizer()
r.load_font('font.bmp')
vidcap = cv2.VideoCapture('../../Flights/12.10/PICT0002.AVI')

f = open('stats.txt', 'w')

vidcap.set(cv2.CAP_PROP_POS_FRAMES,0)

cnt = 0;

while True:
    for i in range(10):
        success, image = vidcap.read()
    if success == 0:
        break;
    cv2.imwrite('frame.png' , image)
    r.load_image('frame.png' )
    s = r.recognize_line((25, 9), 3)
    print(s, ' ', cnt)
    cnt += 1
    f.write(s + '\n')


f.close()


