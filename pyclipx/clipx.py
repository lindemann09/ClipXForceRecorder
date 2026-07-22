from clipx_api import ClipXAPI
from time import sleep
ip = '10.144.71.141'
clipx = ClipXAPI()

clipx.connect(ip)
if clipx.is_connected():

    clipx.start_measurement()
    for x in range(100):
        for _ in range(clipx.available_lines()):
            x = clipx.read_next_line()
            print("---", x)
        else:
            sleep(0.1)
    clipx.stop_measurement()
    clipx.disconnect()

