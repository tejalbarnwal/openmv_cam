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

list_ = [91.1, 92.2, 93.3, 94.4, 95.5, 96.6, 97.7, 88.8, 99.9, 910.10, 11.0, 12.0]

while True:

    command = usb_vcp.recv(4, timeout=5000)

    if command == b'snap':
        image = sensor.snapshot().compress()
        usb_vcp.send(ustruct.pack('<L', image.size()))
        usb_vcp.send(image)
        
        command_d = usb_vcp.recv(4, timeout=5000)
        if command_d == b'list':
        blue_led.on()
        time.sleep(2)
        blue_led.off()
        s = ustruct.pack('12d', *list_)
        usb_vcp.send(s)
        green_led.on()
        time.sleep(2)
        green_led.off()

