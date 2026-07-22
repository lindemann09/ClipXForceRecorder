import ctypes
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Load the ClipXApi library
clipx_api = ctypes.WinDLL('ClipXApi')  # Replace with the full path if needed

# Define the function prototypes (adjust as per ClipX_Interface.h)
clipx_api.ClipX_Connect.argtypes = [ctypes.c_char_p]
clipx_api.ClipX_Connect.restype = ctypes.c_void_p

clipx_api.ClipX_SDOWrite.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p]
clipx_api.ClipX_SDOWrite.restype = None

clipx_api.ClipX_SDORead.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p, ctypes.c_int]
clipx_api.ClipX_SDORead.restype = ctypes.c_int

clipx_api.ClipX_ReadNextBlock.argtypes = [
    ctypes.c_void_p, ctypes.c_int,
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double)
]
clipx_api.ClipX_ReadNextBlock.restype = ctypes.c_int

clipx_api.ClipX_startMeasurement.argtypes = [ctypes.c_void_p]
clipx_api.ClipX_startMeasurement.restype = None

clipx_api.ClipX_stopMeasurement.argtypes = [ctypes.c_void_p]
clipx_api.ClipX_stopMeasurement.restype = None

clipx_api.ClipX_Disconnect.argtypes = [ctypes.c_void_p]
clipx_api.ClipX_Disconnect.restype = None

# Placeholder for signalSelector and getName (implement as needed)
def signalSelector(signals, h):
    # Implement this function based on your ClipXApi requirements
    pass

def getName(signal_index):
    # Implement this function to return the name of the signal
    return f"Signal_{signal_index}"

# Connect to ClipX
ip = b'172.21.104.125'  # Note: MATLAB uses a string, Python uses bytes for c_char_p
h = clipx_api.ClipX_Connect(ip)

# Set parameters
idx = 17448
sidx = 8
samplerate = b'1000'  # Note: MATLAB uses a string, Python uses bytes for c_char_p

# Call SDOWrite and SDORead
clipx_api.ClipX_SDOWrite(h, idx, sidx, samplerate)
intres, readsamplerate = clipx_api.ClipX_SDORead(h, idx, sidx, b'abc', 10)

# Signal indices
signals = [2, 3, 4, 5, 21, 7]
res = signalSelector(signals, h)

# Start measurement
clipx_api.ClipX_startMeasurement(h)

# Initialize arrays for data storage
c = 1000
time = np.zeros(c)
value1 = np.zeros(c)
value2 = np.zeros(c)
value3 = np.zeros(c)
value4 = np.zeros(c)
value5 = np.zeros(c)
value6 = np.zeros(c)

# Prepare pointers for ClipX_ReadNextBlock
time_ptr = (ctypes.c_double * 200)()
value1_ptr = (ctypes.c_double * 200)()
value2_ptr = (ctypes.c_double * 200)()
value3_ptr = (ctypes.c_double * 200)()
value4_ptr = (ctypes.c_double * 200)()
value5_ptr = (ctypes.c_double * 200)()
value6_ptr = (ctypes.c_double * 200)()

# Set up the plot
plt.figure()
plt.grid(True)

# Create subplots for each signal
ax1 = plt.subplot(6, 1, 1)
ax1.set_title('Signal 1')
ax1.set_ylabel('Signal1')

ax2 = plt.subplot(6, 1, 2)
ax2.set_title('Signal 2')

ax3 = plt.subplot(6, 1, 3)
ax3.set_title('Signal 3')

ax4 = plt.subplot(6, 1, 4)
ax4.set_title('Signal 4')

ax5 = plt.subplot(6, 1, 5)
ax5.set_title('Signal 5')

ax6 = plt.subplot(6, 1, 6)
ax6.set_title('Signal 6')
ax6.set_xlabel('Time')

# Initialize lines for animation
line1, = ax1.plot([], [], 'r-')
line2, = ax2.plot([], [], 'y-')
line3, = ax3.plot([], [], 'm-')
line4, = ax4.plot([], [], 'c-')
line5, = ax5.plot([], [], 'b-')
line6, = ax6.plot([], [], 'k-')

# Initialize data buffers
time_buffer = deque(maxlen=200)
value1_buffer = deque(maxlen=200)
value2_buffer = deque(maxlen=200)
value3_buffer = deque(maxlen=200)
value4_buffer = deque(maxlen=200)
value5_buffer = deque(maxlen=200)
value6_buffer = deque(maxlen=200)

ntpbegin = 0

# Function to update the plot
def update(frame):
    global ntpbegin
    count = clipx_api.ClipX_ReadNextBlock(
        h, 200,
        ctypes.byref(time_ptr),
        ctypes.byref(value1_ptr),
        ctypes.byref(value2_ptr),
        ctypes.byref(value3_ptr),
        ctypes.byref(value4_ptr),
        ctypes.byref(value5_ptr),
        ctypes.byref(value6_ptr)
    )

    if frame == 0:
        ntpbegin = time_ptr[0]

    for j in range(count):
        t = time_ptr[j] - ntpbegin
        time_buffer.append(t)
        value1_buffer.append(value1_ptr[j])
        value2_buffer.append(value2_ptr[j])
        value3_buffer.append(value3_ptr[j])
        value4_buffer.append(value4_ptr[j])
        value5_buffer.append(value5_ptr[j])
        value6_buffer.append(value6_ptr[j])

    # Update plot data
    line1.set_data(time_buffer, value1_buffer)
    line2.set_data(time_buffer, value2_buffer)
    line3.set_data(time_buffer, value3_buffer)
    line4.set_data(time_buffer, value4_buffer)
    line5.set_data(time_buffer, value5_buffer)
    line6.set_data(time_buffer, value6_buffer)

    # Adjust plot limits
    for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
        ax.relim()
        ax.autoscale_view()

    return line1, line2, line3, line4, line5, line6

# Create animation
ani = FuncAnimation(plt.gcf(), update, frames=1000, interval=50, blit=True)
plt.tight_layout()
plt.show()

# Stop measurement and disconnect
clipx_api.ClipX_stopMeasurement(h)
clipx_api.ClipX_Disconnect(h)