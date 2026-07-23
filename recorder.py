from time import sleep, time

from .clipx_force_recorder.clipx_api import SIGNAL_LABELS, ClipXAPI, get_signal_id

ip = '10.144.71.141'

v_id = get_signal_id("Field Value")

clipx = ClipXAPI()
clipx.connect(ip)
if clipx.is_connected():
    t_start = time()
    clipx.start_measurement()
    while time()-t_start<5:
        for d in clipx.read_available_blocks():
            print(f"{d.time}, {d.values[v_id]}")
    clipx.stop_measurement()
    clipx.disconnect()

