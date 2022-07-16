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

        list_area = []
        list_0d = []
        list_45d = []
        list_90d = []
        list_135d = []
        list_final = []

        for origin in originList:
            sum_area = 0
            sum_0d = 0
            sum_45d = 0
            sum_90d = 0
            sum_135d = 0

            for i in range(cell_size):
                for j in range(cell_size):

                    intensity = image.get_pixel(origin[0]+i, origin[1]+j)
                    sum_area += intensity < black

                    if (i==origin[0]+(cell_size//2)-1):
                        sum_0d += intensity < black
                    if (i+j == cell_size-1):
                        sum_45d += intensity < black
                    if (j==origin[1]+(cell_size//2)-1):
                        sum_90d += intensity < black
                    if (i==j):
                        sum_135d += intensity < black

            list_area.append(sum_area)
            list_0d.append(sum_0d)
            list_45d.append(sum_45d)
            list_90d.append(sum_90d)
            list_135d.append(sum_135d)

        list_final = list_area + list_0d + list_45d + list_90d + list_135d
        
        image1 = image.compress()
        usb_vcp.send(ustruct.pack('<L', image1.size()))
        usb_vcp.send(image1)
        
        command_d = usb_vcp.recv(4, timeout=5000)

        if command_d == b'list':
            blue_led.on()
            s = ustruct.pack('60d', *list_final)
            usb_vcp.send(s)
            blue_led.off()
