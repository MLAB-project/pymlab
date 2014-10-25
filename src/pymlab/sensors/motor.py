#!/usr/bin/python

# Python driver for MLAB motor driver

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


class MOTOR01(Device):
    """
    Example:



    """

    def __init__(self, parent = None, address = 0x51, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def set_pwm(self,pwm):
        self.bus.write_byte_data(self.address, pwm & 0xFF, (pwm>>8) & 0xFF)


if __name__ == "__main__":
    while True:
        sys.stdout.write("\r\nFrequency: " + self.get_freq() + "     ")
        sys.stdout.flush()
        time.sleep(15)

