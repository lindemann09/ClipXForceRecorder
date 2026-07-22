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
        self.handle = MHandle()

    def connect(self, ip_address: str) -> MHandle:
        """Connect to a ClipX device."""
        print(f"conneting to {ip_address}")
        ip_bytes = ip_address.encode('utf-8')
        self.handle = self.clipx_api.ClipX_Connect(ip_bytes)
        return self.handle

    def sdo_read(self, handle: MHandle, idx: int, subidx: int, val: bytes, size: int) -> None:
        """Read from SDO."""
        self.clipx_api.ClipX_SDORead(handle, idx, subidx, val, size)

    def sdo_write(self, handle: MHandle, idx: int, subidx: int, val: str) -> None:
        """Write to SDO."""
        val_bytes = val.encode('utf-8')
        self.clipx_api.ClipX_SDOWrite(handle, idx, subidx, val_bytes)

    def start_measurement(self, handle: MHandle) -> int:
        """Start measurement."""
        return self.clipx_api.ClipX_startMeasurement(handle)

    def available_lines(self, handle: MHandle) -> int:
        """Get the number of available lines."""
        return self.clipx_api.ClipX_AvailableLines(handle)

    def read_next_line(self, handle: MHandle) -> list:
        """Read the next line of measurement data."""
        mv_line = (c_double * 1)()  # Adjust size as needed
        result = self.clipx_api.ClipX_ReadNextLine(handle, mv_line)
        return list(mv_line) if result > 0 else []

    def read_next_block(
        self, handle: MHandle, max_reads: int
    ) -> tuple:
        """Read the next block of measurement data."""
        time = (c_double * max_reads)()
        value1 = (c_double * max_reads)()
        value2 = (c_double * max_reads)()
        value3 = (c_double * max_reads)()
        value4 = (c_double * max_reads)()
        value5 = (c_double * max_reads)()
        value6 = (c_double * max_reads)()

        count = self.clipx_api.ClipX_ReadNextBlock(
            handle, max_reads,
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

    def stop_measurement(self, handle: MHandle) -> int:
        """Stop measurement."""
        return self.clipx_api.ClipX_stopMeasurement(handle)

    def disconnect(self, handle: MHandle) -> None:
        """Disconnect from the ClipX device."""
        self.clipx_api.ClipX_Disconnect(handle)

    def is_connected(self) -> bool:
        """Check if the device is connected."""
        return self.clipx_api.ClipX_isConnected(self.handle)