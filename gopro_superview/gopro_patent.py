import cv2
import numpy as np

if 0:
    h = 18
    w = 24
    a = 20
    img = np.zeros((a*h, a*w, 3))
    for x in range(w):
        for y in range(h):
            if (x + y) % 2:
                img[a*y:a*(y+1),a*x:a*(x+1), :] = 255

    cv2.imwrite('ch_norm.png', img)
    img = cv2.resize(img, (round(w*a*4/3), h*a))
    cv2.imwrite('ch_wide.png', img)


else:
    im0 = cv2.imread('ch_norm.png')
    im1 = cv2.imread('ch_sv.png')

    im0[:,:,2] = 255
    im0 = im0.astype('float')/255

    x1 = (im1.shape[1] - im0.shape[1]) // 2
    x2 = x1 + im0.shape[1]

    #im1[:, x1:x2, :] = im1[:, x1:x2, :] /2 + im0 / 2
    im1[:, x1:x2, :] = im1[:, x1:x2, :] * im0
    
    cv2.imwrite('ch_overlay.png', im1)
    
    


    
import cv2
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d


img = cv2.imread('ch_wide.png')

height = img.shape[0] 
width = img.shape[1] 

tblH = np.array([0.1107, 0.5340, -1.7813, +1.3167, -0.0722, -0.1073])

tblV = np.array([
    [-0.0749, -0.3167, +1.0939, -0.8113, +0.0408, +0.0678],
    [-0.0658, -0.2785, +0.9617, -0.7132, +0.0359, +0.0596],
    [-0.0568, -0.2402, +0.8294, -0.6152, +0.0309, +0.0514],
    [-0.0444, -0.1880, +0.6491, -0.4814, +0.0242, +0.0403],
    [-0.0337, -0.1427, +0.4928, -0.3655, +0.0184, +0.0306],
    [-0.0296, -0.1253, +0.4327, -0.3209, +0.0161, +0.0268],
    [-0.0337, -0.1427, +0.4928, -0.3655, +0.0184, +0.0306],
    [-0.0444, -0.1880, +0.6491, -0.4814, +0.0242, +0.0403],
    [-0.0568, -0.2402, +0.8294, -0.6152, +0.0309, +0.0514],
    [-0.0658, -0.2785, +0.9617, -0.7132, +0.0359, +0.0596],
    [-0.0749, -0.3167, +1.0939, -0.8113, +0.0408, +0.0678],
    ])

map_x = np.tile(np.arange(width), (height, 1)).astype(np.float32)
map_y = np.tile(np.arange(height), (width, 1)).astype(np.float32).T

deltaYlines = np.array([np.sum(np.array([np.power(xi, np.arange(6,0,-1)) for xi in np.linspace(0, 1, height)]) * t, 1) for t in tblV])
deltaY = -np.array([ np.interp(np.linspace(0,1,width), np.linspace(0,1,11), d) for d in deltaYlines.T])

deltaXline = np.sum(np.array([np.power(xi, np.arange(6,0,-1)) for xi in np.linspace(0, 1, width)]) * tblH, 1)
deltaX = np.tile(deltaXline, (height, 1))

if True:
    X = np.tile(np.linspace(0, 1, width),(height,1))
    Y = np.tile(np.linspace(0, 1, height),(width,1)).T
    
    fig = plt.figure(figsize=(8,4))
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot_surface(X, Y, deltaX, cmap=plt.get_cmap('plasma'))
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot_surface(X, Y, deltaY, cmap=plt.get_cmap('plasma'))
    
    plt.show()



map_x_shift = deltaX * width
map_y_shift = deltaY * height

map_x += map_x_shift
map_y += map_y_shift






img = cv2.remap(np.array(img), map_x, map_y, cv2.INTER_LINEAR)

cv2.imwrite('ch_sv.png', img)














