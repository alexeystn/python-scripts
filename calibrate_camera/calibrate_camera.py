import numpy as np
import cv2 as cv
import glob
import undistort as ud


objp = ud.gen_pattern_grid()
objpoints = []
imgpoints = []

images = glob.glob('/Users/imac/Desktop/calibrate/source/*.png')

for fname in images:
    img = cv.imread(fname)
    img = ud.resize(img)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    ret, corners = cv.findCirclesGrid(gray, (4,11), flags=cv.CALIB_CB_ASYMMETRIC_GRID)
    print(fname, ret)
    
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)
        cv.drawChessboardCorners(img, (4,11), corners, ret)
        ud.show(img, 0.3)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

cv.destroyAllWindows()

with open('calib.npy', 'wb') as f:
    np.save(f, mtx)
    np.save(f, dist)

