#!/usr/bin/python

# Python driver for MLAB DRV10987 module

import math
import time
import sys
import logging
import time

from MLAB_DRV10987 import MLAB_DRV10987
from MLAB_DRV10987 import print_status_registers

from pymlab.sensors import Device

import struct

LOGGER = logging.getLogger(__name__)


class DRV10987(Device, MLAB_DRV10987):
    def __init__(self, parent=None, address=112, **kwargs):
        Device.__init__(self, address=address)
        print("INIT...")
        print(self.bus)
        MLAB_DRV10987.__init__(self, self.bus, addr=address, initialize=False)