"""ClipX API wrapper for Python.

Oliver Lindemann
"""

from ctypes import *
from dataclasses import dataclass
from typing import List

NO_CLIPX_ERROR = "ClipX not connected!"

SIGNAL_LABELS = {
    0: 'ADC Value',
    1: 'Filtered ADC Value',
    2: 'Field Value',
    3: 'Gross Value',
    4: 'Net Value',
    5: 'Min Value',
    6: 'Max Value',
    7: 'Peak Peak Value',
    8: 'Captured Value 1',
    9: 'Captured Value 2',
    10: 'ClipX Bus Value 1',
    11: 'ClipX Bus Value 2',
    12: 'ClipX Bus Value 3',
    13: 'ClipX Bus Value 4',
    14: 'ClipX Bus Value 5',
    15: 'ClipX Bus Value 6',
    16: '',
    17: '',
    18: '',
    19: '',
    20: '',
    21: 'Calculated Value 1',
    22: 'Calculated Value 2',
    23: 'Calculated Value 3',
    24: 'Calculated Value 4',
    25: 'Calculated Value 5',
    26: 'Calculated Value 6',
    27: 'Ethernet API 1',
    28: 'Ethernet API 2',
    29: 'Fieldbus Value 1',
    30: 'Fieldbus Value 2',
    31: 'Analog Out Value',
    32: 'Constant -1',
    33: 'Constant 0',
    34: 'Constant 1',
    35: 'Constant PI/2',
    36: 'Constant PI',
    37: 'Constant 2*PI',
    38: 'User Constant 1',
    39: 'User Constant 2',
    40: 'User Constant 3',
    41: 'User Constant 4',
    42: 'User Constant 5',
    43: 'User Constant 6',
    44: 'User Constant 7',
    45: 'User Constant 8',
    46: 'User Constant 9',
    47: 'User Constant 10'
}

def get_signal_id(label:str) -> int:
    for (i, v) in SIGNAL_LABELS.items():
        if v==label:
            return i
    raise ValueError(f"Unknown signal label: {label}")

@dataclass
class ClipXData:
    time: float
    values: List[float]


# Define the MHandle type (pointer to sClipX)
class sClipX(Structure):
    _fields_ = [("obj", c_void_p)]

MHandle = POINTER(sClipX)

class ClipXAPI(object):

    def __init__(self, dll_path: str = "./ClipXApi.dll"):
        self.clipx_api = WinDLL(dll_path)

        self.clipx_api.ClipX_Connect.argtypes = [c_char_p]
        self.clipx_api.ClipX_Connect.restype = MHandle

        # ClipX_SDORead
        self.clipx_api.ClipX_SDORead.argtypes = [MHandle, c_int, c_int, c_char_p, c_int]
        self.clipx_api.ClipX_SDORead.restype = None

        # ClipX_SDOWrite
        self.clipx_api.ClipX_SDOWrite.argtypes = [MHandle, c_int, c_int, c_char_p]
        self.clipx_api.ClipX_SDOWrite.restype = None

        # ClipX_startMeasurement
        self.clipx_api.ClipX_startMeasurement.argtypes = [MHandle]
        self.clipx_api.ClipX_startMeasurement.restype = c_int

        # ClipX_AvailableLines
        self.clipx_api.ClipX_AvailableLines.argtypes = [MHandle]
        self.clipx_api.ClipX_AvailableLines.restype = c_int

        # ClipX_ReadNextLine
        self.clipx_api.ClipX_ReadNextLine.argtypes = [MHandle, POINTER(c_double)]
        self.clipx_api.ClipX_ReadNextLine.restype = c_int

        # ClipX_ReadNextBlock
        self.clipx_api.ClipX_ReadNextBlock.argtypes = [
            MHandle, c_int,
            POINTER(c_double), POINTER(c_double),
            POINTER(c_double), POINTER(c_double),
            POINTER(c_double), POINTER(c_double),
            POINTER(c_double)
        ]
        self.clipx_api.ClipX_ReadNextBlock.restype = c_int

        # ClipX_stopMeasurement
        self.clipx_api.ClipX_stopMeasurement.argtypes = [MHandle]
        self.clipx_api.ClipX_stopMeasurement.restype = c_int

        # ClipX_Disconnect
        self.clipx_api.ClipX_Disconnect.argtypes = [MHandle]
        self.clipx_api.ClipX_Disconnect.restype = None

        # ClipX_isConnected
        self.clipx_api.ClipX_isConnected.argtypes = [MHandle]
        self.clipx_api.ClipX_isConnected.restype = c_bool

        self.handle = None

    def connect(self, ip_address: str):
        """Connect to a ClipX device."""
        print(f"conneting to {ip_address}")
        ip_bytes = ip_address.encode('utf-8')
        handle = self.clipx_api.ClipX_Connect(ip_bytes)
        if not handle:
            raise RuntimeError("failed to connect to deivce.")
        else:
            self.handle = handle
    def sdo_read(self, idx: int, subidx: int, val: bytes, size: int) -> None:
        """Read from SDO."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        self.clipx_api.ClipX_SDORead(self.handle, idx, subidx, val, size)

    def sdo_write(self, idx: int, subidx: int, val: str) -> None:
        """Write to SDO."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        val_bytes = val.encode('utf-8')
        self.clipx_api.ClipX_SDOWrite(self.handle, idx, subidx, val_bytes)

    def start_measurement(self) -> int:
        """Start measurement."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        return self.clipx_api.ClipX_startMeasurement(self.handle)

    def available_lines(self) -> int:
        """Get the number of available lines."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        return self.clipx_api.ClipX_AvailableLines(self.handle)

    def read_next_line(self) -> list:
        """Read the next line of measurement data."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        mv_line = (c_double * 1)()  # Adjust size as needed
        result = self.clipx_api.ClipX_ReadNextLine(self.handle, mv_line)
        return mv_line if result > 0 else []

    def read_next_block(self, max_reads: int) -> ClipXData:
        """Read the next block of measurement data."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        time = (c_double * max_reads)()
        value1 = (c_double * max_reads)()
        value2 = (c_double * max_reads)()
        value3 = (c_double * max_reads)()
        value4 = (c_double * max_reads)()
        value5 = (c_double * max_reads)()
        value6 = (c_double * max_reads)()

        count = self.clipx_api.ClipX_ReadNextBlock(
            self.handle, max_reads,
            time, value1,
            value2, value3,
            value4, value5,
            value6
        )

        rtn = []
        for c in range(count):
            rtn.append(ClipXData(time[c],
                                 [value1[c], value2[c], value3[c], 
                                  value4[c], value5[c], value6[c]]))
                                
        return rtn

    def read_available_blocks(self) -> List[ClipXData]:
        n = self.available_lines()
        if n>0:
            return self.read_next_block(n)
        else:
            return []

    def stop_measurement(self) -> int:
        """Stop measurement."""
        if self.handle is None:
            raise RuntimeError(NO_CLIPX_ERROR)
        return self.clipx_api.ClipX_stopMeasurement(self.handle)

    def disconnect(self) -> None:
        """Disconnect from the ClipX device."""
        if self.handle is None:
            return
        self.clipx_api.ClipX_Disconnect(self.handle)
        self.handle = None

    def is_connected(self) -> bool:
        """Check if the device is connected."""
        if self.handle is None:
            return False
        else:
            return self.clipx_api.ClipX_isConnected(self.handle)


## Helper functions
def signalSelector(signals, h): ### FIXME NOT TESTED
    """
    This function sets up the signals for the FIFO storage to be monitored.
    ClipX must already be connected.

    Args:
        signals (list): List of signal indices to configure.
        h (ctypes.c_void_p): Handle to the ClipX connection.

    Returns:
        int: 1 if successful, -1 if ClipX is not connected.
    """
    # Load the ClipXApi library (assuming it's already loaded)
    clipx_api = ctypes.WinDLL('ClipXApi')

    # Define the function prototypes
    clipx_api.ClipX_isConnected.argtypes = [ctypes.c_void_p]
    clipx_api.ClipX_isConnected.restype = ctypes.c_bool

    clipx_api.ClipX_SDOWrite.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p]
    clipx_api.ClipX_SDOWrite.restype = None

    # Constants
    idx = 17448
    sidx1 = 5
    sidx2 = 7

    # Check if ClipX is connected
    if not clipx_api.ClipX_isConnected(h):
        return -1

    # Configure each signal
    for i in range(6):
        iin = str(i + 1).encode('utf-8')  # Convert to bytes for c_char_p
        sin = str(signals[i]).encode('utf-8')  # Convert to bytes for c_char_p

        clipx_api.ClipX_SDOWrite(h, idx, sidx1, iin)
        clipx_api.ClipX_SDOWrite(h, idx, sidx2, sin)

    return 1
