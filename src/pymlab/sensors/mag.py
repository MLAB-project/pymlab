#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class
# This code is adopted from: 

import math
import time
import sys

from pymlab.sensors import Device


class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class MAG01(Device):
    """
    Example:
    
    """

    SCALES = {
        0.88: [0, 0.73],
        1.30: [1, 0.92],
        1.90: [2, 1.22],
        2.50: [3, 1.52],
        4.00: [4, 2.27],
        4.70: [5, 2.56],
        5.60: [6, 3.03],
        8.10: [7, 4.35],
    }

    def __init__(self, parent = None, address = 0x1E, gauss = 1.3, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self._gauss = gauss
        (reg, self._scale) = self.SCALES[gauss]

    def twos_complement(self, val, len):
        # Convert twos compliment to integer
        if (val & (1 << len - 1)):
            val = val - (1<<len)
        return val

    def _convert(self, data, offset):
        val = self.twos_complement(data[offset] << 8 | data[offset+1], 16)
        if val == -4096: return Over
        return round(val * self._scale, 4)

    def initialize(self):
        reg, self._scale = self.SCALES[self._gauss]
        
        self.bus.write_byte_data(self.address, 0x00, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, 0x01, reg << 5) # Scale
        self.bus.write_byte_data(self.address, 0x02, 0x00) # Continuous measurement

    def axes(self):
        data = self.bus.read_block_data(self.address, 0x00)
        #print map(hex, data)
        x = self._convert(data, 3)
        y = self._convert(data, 7)
        z = self._convert(data, 5)
        return (x,y,z)

    def __str__(self):
        (x, y, z) = self.axes()
        return "Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n" \


