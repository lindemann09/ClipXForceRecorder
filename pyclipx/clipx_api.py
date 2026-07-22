"""ClipX API wrapper for Python.

Oliver Lindemann
"""

from ctypes import *


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
        self.handle = self.clipx_api.ClipX_Connect(ip_bytes)

    def sdo_read(self, idx: int, subidx: int, val: bytes, size: int) -> None:
        """Read from SDO."""
        self.clipx_api.ClipX_SDORead(self.handle, idx, subidx, val, size)

    def sdo_write(self, idx: int, subidx: int, val: str) -> None:
        """Write to SDO."""
        val_bytes = val.encode('utf-8')
        self.clipx_api.ClipX_SDOWrite(self.handle, idx, subidx, val_bytes)

    def start_measurement(self) -> int:
        """Start measurement."""
        return self.clipx_api.ClipX_startMeasurement(self.handle)

    def available_lines(self) -> int:
        """Get the number of available lines."""
        return self.clipx_api.ClipX_AvailableLines(self.handle)

    def read_next_line(self) -> list:
        """Read the next line of measurement data."""
        mv_line = (c_double * 1)()  # Adjust size as needed
        result = self.clipx_api.ClipX_ReadNextLine(self.handle, mv_line)
        return list(mv_line) if result > 0 else []

    def read_next_block(self, max_reads: int) -> tuple:
        """Read the next block of measurement data."""
        time = (c_double * max_reads)()
        value1 = (c_double * max_reads)()
        value2 = (c_double * max_reads)()
        value3 = (c_double * max_reads)()
        value4 = (c_double * max_reads)()
        value5 = (c_double * max_reads)()
        value6 = (c_double * max_reads)()

        count = self.clipx_api.ClipX_ReadNextBlock(
            self.handle, max_reads,
            byref(time), byref(value1),
            byref(value2), byref(value3),
            byref(value4), byref(value5),
            byref(value6)
        )

        return (
            count,
            list(time), list(value1), list(value2),
            list(value3), list(value4), list(value5), list(value6)
        )

    def stop_measurement(self) -> int:
        """Stop measurement."""
        return self.clipx_api.ClipX_stopMeasurement(self.handle)

    def disconnect(self) -> None:
        """Disconnect from the ClipX device."""
        self.clipx_api.ClipX_Disconnect(self.handle)

    def is_connected(self) -> bool:
        """Check if the device is connected."""
        return self.clipx_api.ClipX_isConnected(self.handle)

