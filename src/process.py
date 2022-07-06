import io
import struct
import sys

import numpy as np
import serial
from PIL import Image as PILImage
import matplotlib.pyplot as plt


class OpenMVCamRead:

    def __init__(self, device='/dev/ttyACM0'):
        self.port = serial.Serial(device, baudrate=115200,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  xonxoff=False, rtscts=False,
                                  stopbits=serial.STOPBITS_ONE,
                                  timeout=None, dsrdtr=True)

        self.port.reset_input_buffer()
        self.port.reset_output_buffer()

        self.initial_matrix = None

    def read(self):
        snap = 'snap'
        if sys.version_info[0] >= 3:
            snap = snap.encode('utf-8')
        self.port.write(snap)
        self.port.flush()

        print("SNAP")

        size = struct.unpack('<L', self.port.read(4))[0]
        image_data = self.port.read(size)
        image = np.array(PILImage.open(io.BytesIO(image_data)))

        print("IMAGE DATA")

        list_ = 'list'
        if sys.version_info[0] >= 3:
            list_ = list_.encode('utf-8')
        self.port.write(list_)
        self.port.flush()

        print("LIST")

        list_ = struct.unpack('12d', self.port.read(96))

        print(len(list_))

        return image, list_

    def intialize(self, list_):
        self.initial_matrix = (np.array(list_)).reshape((4,3)).transpose()


    def store(self, image, list_):

        matrix = (np.array(list_)).reshape((4,3)).transpose()
        deform_matrix = matrix # - self.initial_matrix
        figure, axis = plt.subplots(2, 1)
        axis[0].imshow(deform_matrix, cmap='gray', vmin=0, vmax=320)
        axis[1].imshow(image,cmap='gray')
        plt.savefig('store.png')


if __name__ == '__main__':
    instance = OpenMVCamRead()

    # image, list_ = instance.read()
    # instance.initial_matrix = instance.intialize(list_)

    while (True):
        image, list_ = instance.read()
        instance.store(image, list_)