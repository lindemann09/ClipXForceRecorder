"""
Recording and streaming ClipX Force Sensors with Python and Lab Streaming Layer (LSL).
"""

from importlib.metadata import version

from .misc import set_logging as _set_logging

APPNAME = "clipx_force_recorder"
__version__ = version(APPNAME)
__author__ = "Oliver Lindemann"

LOGFILE = _set_logging(log_file=f"{APPNAME}.log") # TODO: logging

