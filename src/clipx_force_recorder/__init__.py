"""
Recording and streaming ClipX Force Sensors with Python and Lab Streaming Layer (LSL).
"""

from importlib.metadata import version

from .tools import _log

APPNAME = "clipx_force_recorder"
__version__ = version(APPNAME)
__author__ = "Oliver Lindemann"

LOGFILE = _log.set_logging(log_file=f"{APPNAME}.log")

