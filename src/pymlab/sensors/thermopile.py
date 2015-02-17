#!/usr/bin/python

# Python driver for MLAB Thermopile module

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


class THERMOPILE01(Device):

    def __init__(self, parent = None, address = 0x5A, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def setAddress(self, address):
        self.address = address;

    def getTambient(self):
        return self.bus.read_word_data(self.address, 0x06) * 0.02 - 273.15;        

    def getTobject1(self):
        return self.bus.read_word_data(self.address, 0x07) * 0.02 - 273.15;

    def getTobject2(self):
        return self.bus.read_word_data(self.address, 0x08) * 0.02 - 273.15;


