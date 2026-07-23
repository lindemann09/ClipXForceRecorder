"""
Recording and streaming ClipX Force Sensors with Python and Lab Streaming Layer (LSL).
"""

from importlib.metadata import version

from .force_sensor import ClipXForceSensor
from .settings import RecordingSettings

__version__ = version("clipx_force_recorder")
__author__ = "Oliver Lindemann"
