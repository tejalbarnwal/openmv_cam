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


cell_size = 80
origin = 0
originList = [(origin+c*(cell_size), origin+r*(cell_size)) for c in range(4) for r in range(3)]
black = 60

while True:
    command = usb_vcp.recv(4, timeout=5000)

    if command == b'snap':
        image = sensor.snapshot()

        count = []
        for origin in originList:
            sum_ = 0
            for i in range(cell_size):
                for j in range(cell_size):
                    sum_ += (image.get_pixel(origin[0]+i, origin[1]+j)) < black
                    
            count.append(sum_)
        
        image1 = image.compress()
        usb_vcp.send(ustruct.pack('<L', image1.size()))
        usb_vcp.send(image1)
        
        command_d = usb_vcp.recv(4, timeout=5000)

        if command_d == b'list':
            blue_led.on()
            s = ustruct.pack('12d', *count)
            usb_vcp.send(s)
            blue_led.off()