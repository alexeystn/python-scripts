import ctypes
import numpy as np
from matplotlib import pyplot as plt

# build .so from .c source:
# gcc -shared -o my_lib.so my_lib.c

lib = ctypes.CDLL('my_lib.so')

length = 9

array_x = np.linspace(-1, 1, length).astype('float32')
pointer_x = array_x.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

array_y = np.zeros((length,), dtype='float32')
pointer_y = array_y.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

# y = x^2
lib.square(pointer_x, pointer_y, length)

plt.plot(array_x, array_y, '.-')
plt.grid(True)
plt.show()
