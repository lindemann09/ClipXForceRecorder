from clipx_api import ClipXAPI

ip = '10.144.71.14';
clipx = ClipXAPI()
x = clipx.connect(ip)
print("x")
clipx.disconnect(x)