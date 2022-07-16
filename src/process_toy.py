import io
import struct
import sys

import numpy as np
import serial
from PIL import Image as PILImage
import matplotlib.pyplot as plt

import cv2


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

        self.initial_matrix = np.zeros((3,4), dtype=np.float64)

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

        list_ = struct.unpack('48d', self.port.read(384))
        print(list_)

        return image, list_


    def store(self, image, list_, count):
        matrix = (np.array(list_)).reshape((4,3)).transpose() 
        deform_matrix = matrix - self.initial_matrix
        print("\n Difference pixel count:\n")
        print(deform_matrix)
        figure, axis = plt.subplots(2, 1)
        axis[0].imshow(deform_matrix, cmap='gray', vmin=0, vmax=1000)
        image = self.plot_mesh(image)
        axis[1].imshow(image,cmap='gray')
        plt.savefig("store.png")
        # name = "/home/tejal/catkin_ws/src/openmv_cam/TestDataset/store"+str(count)+".png"
        # plt.savefig(name)

        figure1, axis1 = plt.subplots(1, 1)

        axis1.imshow(image,cmap='gray')
        plt.savefig("storeimg.png")


if __name__ == '__main__':
    instance = OpenMVCamRead()

    while (True):
        image, list_ = instance.read()