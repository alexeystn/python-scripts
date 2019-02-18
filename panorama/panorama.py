import cv2
import numpy
import sys

from numpy import pi
from PIL import Image

# Convert using an inverse transformation
def generate_mapping_data(image_width):
    in_size = [image_width, image_width * 3 // 4]
    edge = in_size[0] // 4  # The length of each edge in pixels

    # Create our numpy arrays
    out_pix = numpy.zeros((in_size[1], in_size[0], 2), dtype="f4")
    xyz = numpy.zeros((in_size[1] * in_size[0] // 2, 3), dtype="f4")
    vals = numpy.zeros((in_size[1] * in_size[0] // 2, 3), dtype="i4")

    # Much faster to use an arange when we assign to to vals
    start, end = 0, 0
    rng_1 = numpy.arange(0, edge * 3)
    rng_2 = numpy.arange(edge, edge * 2)
    for i in range(in_size[0]):
        # 0: back
        # 1: left
        # 2: front
        # 3: right
        face = int(i / edge)
        rng = rng_1 if face == 2 else rng_2

        end += len(rng)
        vals[start:end, 0] = rng
        vals[start:end, 1] = i
        vals[start:end, 2] = face
        start = end

    # Top/bottom are special conditions
    j, i, face = vals.T
    face[j < edge] = 4  # top
    face[j >= 2 * edge] = 5  # bottom

    # Convert to image xyz
    a = 2.0 * i / edge
    b = 2.0 * j / edge
    one_arr = numpy.ones(len(a))
    for k in range(6):
        face_idx = face == k

        # Using the face_idx version of each is 50% quicker
        one_arr_idx = one_arr[face_idx]
        a_idx = a[face_idx]
        b_idx = b[face_idx]

        if k == 0:
           vals_to_use =  [-one_arr_idx, 1.0 - a_idx, 3.0 - b_idx]
        elif k == 1:
           vals_to_use =  [a_idx - 3.0, -one_arr_idx, 3.0 - b_idx]
        elif k == 2:
           vals_to_use =  [one_arr_idx, a_idx - 5.0, 3.0 - b_idx]
        elif k == 3:
           vals_to_use =  [7.0 - a_idx, one_arr_idx, 3.0 - b_idx]
        elif k == 4:
           vals_to_use =  [b_idx - 1.0, a_idx - 5.0, one_arr_idx]
        elif k == 5:
           vals_to_use =  [5.0 - b_idx, a_idx - 5.0, -one_arr_idx]

        xyz[face_idx] = numpy.array(vals_to_use).T

    # Convert to theta and pi
    x, y, z = xyz.T
    theta = numpy.arctan2(y, x)
    r = numpy.sqrt(x**2 + y**2)
    phi = numpy.arctan2(z, r)

    # Source img coords
    uf = (2.0 * edge * (theta + pi) / pi) % in_size[0]
    uf[uf==in_size[0]] = 0.0 # Wrap to pixel 0 (much faster than modulus)
    vf = (2.0 * edge * (pi / 2 - phi) / pi)

    # Mapping matrix
    out_pix[j, i, 0] = vf
    out_pix[j, i, 1] = uf

    map_x_32 = out_pix[:, :, 1]
    map_y_32 = out_pix[:, :, 0]
    return map_x_32, map_y_32

name = 'Panorama.jpg'
imgIn = Image.open(name)
inSize = imgIn.size

map_x_32, map_y_32 = generate_mapping_data(inSize[0])
cubemap = cv2.remap(numpy.array(imgIn), map_x_32, map_y_32, cv2.INTER_LINEAR)

imgOut = Image.fromarray(cubemap)
imgOut.save(name.split('.')[0]+"_out.png")
imgOut.show()
