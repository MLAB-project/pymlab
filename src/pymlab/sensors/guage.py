#!/usr/bin/python

# Python driver for MLAB LiIon Cell Guage

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


class LIION1CELL01(Device):

    def __init__(self, parent = None, address = 0x5A, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    
    # Reading temperature of device case in Celsius
    def getMft(self):
        print hex(self.bus.read_byte_data(self.address, 0x07)
        return         

    # Reading of temperature of distant object from zone 1 in Celsius
    def getTobject1(self):
        return self.bus.read_word_data(self.address, 0x07) * 0.02 - 273.15;

    # Reading of temperature of distant object from zone 2 in Celsius
    def getTobject2(self):
        return self.bus.read_word_data(self.address, 0x08) * 0.02 - 273.15;


