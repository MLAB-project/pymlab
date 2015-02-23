#!/usr/bin/python

# Python driver for MLAB LION1CELL01B module

import math
import time
import sys
import logging
import time

from pymlab.sensors import Device

import struct

LOGGER = logging.getLogger(__name__)

class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class LION1CELL01(Device):
    """
    Battery Guage binding
    
    """

    def __init__(self, parent = None, address = 0x55, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    # deg C
    def getTemp(self):           
        return (self.bus.read_byte_data(self.address, 0x0C) + self.bus.read_byte_data(self.address, 0x0D) * 256) * 0.1 - 273.15

    # mAh
    def getRemainingCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x04) + self.bus.read_byte_data(self.address, 0x05) * 256)

    # mAh
    def FullChargeCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x06) + self.bus.read_byte_data(self.address, 0x07) * 256)

    # V
    def Voltage(self):
        return (self.bus.read_byte_data(self.address, 0x08) + self.bus.read_byte_data(self.address, 0x09) * 256)

    # %
    def StateOfCharge(self):
        return (self.bus.read_byte_data(self.address, 0x02) + self.bus.read_byte_data(self.address, 0x03) * 256)


    # mA
    def AverageCurrent(self):
        I = (self.bus.read_byte_data(self.address, 0x0A) + self.bus.read_byte_data(self.address, 0x0B) * 256)
        if (I & 0x8000):
            return -0x10000 + I
        else:
            return I


