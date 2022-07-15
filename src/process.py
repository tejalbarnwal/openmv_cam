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

        list_ = struct.unpack('12d', self.port.read(96))

        print(len(list_))

        # list_ = [0,0,0,0,0,0,0,0,0,0,0,0]

        return image, list_

    def plot_mesh(self, image):
        cell_size = 80 
        numCRows = image.shape[0]// cell_size  
        numCColumns = image.shape[1]// cell_size
        # print("Size of circle grid:", numCRows, "X", numCColumns)

        # centers list
        CCenterList = [(40+c*(80), 40+r*(80)) for c in range(numCColumns) for r in range(numCRows)]
        # print(CCenterList)

        # visulaization
        for c in CCenterList:
          image = cv2.circle(image, c, 1, (255, 0, 0), -1)
          image = cv2.rectangle(image, (c[0]-40, c[1]-40), (c[0]+40, c[1]+40), (0, 255, 0), 1)

        return image


    def intialize(self, image, list_):
        matrix = (np.array(list_)).reshape((4,3)).transpose()
        self.initial_matrix = matrix
        figure, axis = plt.subplots(1, 1)

        image = self.plot_mesh(image)

        axis.imshow(image,cmap='gray')
        plt.savefig("original_store.png")
        # plt.savefig('/home/tejal/catkin_ws/src/openmv_cam/TestDataset/store00.png')
        return self.initial_matrix


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

    key_input = input("Initialize?")

    if key_input.lower()=="y":
        image, list_ = instance.read()
        instance.initial_matrix = instance.intialize(image, list_)

    imgCount = 1
    while (True):
        image, list_ = instance.read()
        instance.store(image, list_, imgCount)
        imgCount+=1