#!/usr/bin/python

# Python driver for MLAB frequency counter design wrapper class

import math
import time
import sys
import struct

from pymlab.sensors import Device


class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class ACOUNTER02(Device):
    """
    Example:



    """

    def __init__(self, parent = None, address = 0x51, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def read_count(self):
        b0 = self.bus.read_byte_data(self.address, 0x00)
        b1 = self.bus.read_byte_data(self.address, 0x01)
        b2 = self.bus.read_byte_data(self.address, 0x02)
        b3 = self.bus.read_byte_data(self.address, 0x03)
        count = bytes(bytearray([b3, b2, b1, b0]))
        return struct.unpack(">L", count)[0]

    def get_freq(self):
        count = self.read_count()
        return (count/(10.0 - 100.0e-6))         #convert  ~10s  of pulse counting to  frequency


if __name__ == "__main__":
    while True:
        sys.stdout.write("\r\nFrequency: " + self.get_freq() + "     ")
        sys.stdout.flush()
        time.sleep(15)

