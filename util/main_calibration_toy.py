import sensor, ustruct, pyb, time

usb_vcp = pyb.USB_VCP()
usb_vcp.setinterrupt(-1)

green_led = pyb.LED(2)
blue_led  = pyb.LED(3)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.skip_frames(time=2000) 


while True:
    command = usb_vcp.recv(4, timeout=5000)

    if command == b'snap':
        image = sensor.snapshot()

        list_0d = []
        list_45d = []
        list_90d = []
        list_135d = []
        list_final = []

        for i in range(12):
            list_0d.append(i)
            list_45d.append(i+12)
            list_90d.append(i+24)
            list_135d.append(i+36)

        list_final = list_0d + list_45d + list_90d + list_135d
        
        image1 = image.compress()
        usb_vcp.send(ustruct.pack('<L', image1.size()))
        usb_vcp.send(image1)
        
        command_d = usb_vcp.recv(4, timeout=5000)

        if command_d == b'list':
            blue_led.on()
            s = ustruct.pack('48d', *list_final)
            usb_vcp.send(s)
            blue_led.off()