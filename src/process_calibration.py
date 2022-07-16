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

        self.initArea = np.zeros((3,4), dtype=np.float64)
        self.init0d = np.zeros((3,4), dtype=np.float64)
        self.init45d = np.zeros((3,4), dtype=np.float64)
        self.init90d = np.zeros((3,4), dtype=np.float64)
        self.init135d = np.zeros((3,4), dtype=np.float64)
        self.initPlusCross = np.zeros((3,4), dtype = np.float64)


    def readFromNicla(self):
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

        list_ = struct.unpack('60d', self.port.read(480))

        return image, list_

    def plot_mesh(self, image):
        cell_size = 80 
        numCRows = image.shape[0]// cell_size  
        numCColumns = image.shape[1]// cell_size
        CCenterList = [(40+c*(80), 40+r*(80)) for c in range(numCColumns) for r in range(numCRows)]

        for c in CCenterList:
          image = cv2.circle(image, c, 1, (255, 0, 0), -1)
          image = cv2.rectangle(image, (c[0]-40, c[1]-40), (c[0]+40, c[1]+40), (0, 255, 0), 1)

        return image


    def intialize(self, image, list_):
        matrixArea = (np.array(list_[0:12])).reshape((4,3)).transpose()
        matrix0d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrix45d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrix90d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrix135d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrixPlusCross = matrix0d + matrix45d + matrix90d + matrix135d

        self.initArea = matrixArea
        self.init0d = matrix0d
        self.init45d = matrix45d
        self.init90d = matrix90d
        self.init135d = matrix135d
        self.initPlusCross = matrixPlusCross

        figure, axis = plt.subplots(1, 1)
        image = self.plot_mesh(image)
        axis.imshow(image,cmap='gray')
        # plt.savefig("original_store.png")
        plt.savefig('/home/tejal/catkin_ws/src/openmv_cam/TestDataset/store00.png')

        dumpFile = open("/home/tejal/catkin_ws/src/openmv_cam/TestDataset/dump00.txt", "a")
        dumpFile.write("\n Area Matrix:\n" + str(matrixArea) + "\n")
        dumpFile.write("\n - Matrix:\n" + str(matrix0d) + "\n")
        dumpFile.write("\n / Matrix:\n" + str(matrix45d) + "\n")
        dumpFile.write("\n | Matrix:\n" + str(matrix90d) + "\n")
        dumpFile.write("\n \\ Matrix:\n" + str(matrix135d) + "\n")
        dumpFile.write("\n Plus Cross Matrix:\n" + str(matrixPlusCross) + "\n")


    def interpretAndStore(self, image, list_, imgCount):

        if imgCount < 10:
            count = "0" + str(imgCount)
        else:
            count = str(imgCount)

        matrixArea = (np.array(list_[0:12])).reshape((4,3)).transpose()
        matrix0d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrix45d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrix90d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrix135d = (np.array(list_[12:24])).reshape((4,3)).transpose()
        matrixPlusCross = matrix0d + matrix45d + matrix90d + matrix135d

        deformArea = matrixArea - self.initArea
        deform0d = matrix0d - self.init0d
        deform45d = matrix45d - self.init45d
        deform90d = matrix90d - self.init90d
        deform135d = matrix135d - self.init135d
        deformPlusCross = matrixPlusCross - self.initPlusCross

        # plot
        figure, axis = plt.subplots(2, 2)
        axis[0][0].imshow(deformArea, cmap = "gray", vmin=0, vmax=1000)
        axis[0][0].set_title("Deformation/ Chnage in Area")
        axis[1][0].imshow(deformPlusCross, cmap="gray", vmin=0, vmax=1000)
        axis[1][0].set_title("Defromation in Plus and Cross")
        image = self.plot_mesh(image)
        axis[0][1].imshow(image,cmap='gray')
        # plt.savefig("deformation_img.png")
        name_fig = "/home/tejal/catkin_ws/src/openmv_cam/TestDataset/store" + count + ".png"
        plt.savefig(name_fig)

        # dump to file
        name_txt = "/home/tejal/catkin_ws/src/openmv_cam/TestDataset/dump" + count + ".txt"
        dumpFile = open(name_txt, "a")

        dumpFile.write("\n Area Matrix:\n" + str(matrixArea) + "\n")
        dumpFile.write("\n - Matrix:\n" + str(matrix0d) + "\n")
        dumpFile.write("\n / Matrix:\n" + str(matrix45d) + "\n")
        dumpFile.write("\n | Matrix:\n" + str(matrix90d) + "\n")
        dumpFile.write("\n \\ Matrix:\n" + str(matrix135d) + "\n")
        dumpFile.write("\n Plus Cross Matrix:\n" + str(matrixPlusCross) + "\n")

        dumpFile.write("\nDeform Area Matrix:\n" + str(deformArea) + "\n")
        dumpFile.write("\nDefrom - Matrix:\n" + str(deform0d) + "\n")
        dumpFile.write("\nDefrom / Matrix:\n" + str(deform45d) + "\n")
        dumpFile.write("\nDefrom | Matrix:\n" + str(deform90d) + "\n")
        dumpFile.write("\nDefrom \\ Matrix:\n" + str(deform135d) + "\n")
        dumpFile.write("\nDefrom Plus Cross Matrix:\n" + str(deformPlusCross) + "\n")

        dumpFile.close()


if __name__ == '__main__':
    instance = OpenMVCamRead()

    key_input = input("Initialize?")

    if key_input.lower()=="y":
        image, list_ = instance.readFromNicla()
        instance.intialize(image, list_)

    imgCount = 1
    while (True):
        image, list_ = instance.readFromNicla()
        instance.interpretAndStore(image, list_, imgCount)
        imgCount+=1