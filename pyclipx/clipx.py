from clipx_api import ClipXAPI
from time import sleep
ip = '10.144.71.141'
clipx = ClipXAPI()
x = clipx.connect(ip)
print(x)
print(type(x))
sleep(1)

print(clipx.is_connected())
clipx.disconnect(x)