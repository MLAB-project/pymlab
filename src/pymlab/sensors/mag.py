#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class
# This code is adopted from: 

import math
import time
import sys
import logging

from pymlab.sensors import Device


LOGGER = logging.getLogger(__name__)

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

    def __init__(self, parent = None, address = 0x1E, gauss = 4.0, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self._gauss = gauss
        (reg, self._scale) = self.SCALES[gauss]

        self.HMC5883L_CRA    =0x00
        self.HMC5883L_CRB    =0x01
        self.HMC5883L_MR     =0x02
        self.HMC5883L_DXRA   =0x03
        self.HMC5883L_DXRB   =0x04
        self.HMC5883L_DYRA   =0x05
        self.HMC5883L_DYRB   =0x06
        self.HMC5883L_DZRA   =0x07
        self.HMC5883L_DZRB   =0x08
        self.HMC5883L_SR     =0x09
        self.HMC5883L_IRA    =0x0A
        self.HMC5883L_IRB    =0x0B
        self.HMC5883L_IRC    =0x0C

    def initialize(self):
        reg, self._scale = self.SCALES[self._gauss]
        self.bus.read_byte(self.address)
        self.bus.write_byte_data(self.address, self.HMC5883L_CRA, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, self.HMC5883L_CRB, reg << 5) # Scale
        self.bus.write_byte_data(self.address, self.HMC5883L_MR, 0x00) # Continuous measurement
        LOGGER.debug("Byte data %s to register %s to address %s writen",
            bin(self.bus.read_byte_data(self.address, self.HMC5883L_MR)), hex(self.HMC5883L_MR), hex(self.address))

        self.x = [0, 0, 0] # min, max, offset
        self.y = [0, 0, 0]
        self.z = [0, 0, 0]

    def axes(self, offset = False):
        """returns measured value in miligauss"""
        reg, self._scale = self.SCALES[self._gauss]
        x = self.bus.read_int16_data(self.address, self.HMC5883L_DXRA) 
        if x == -4096: x = OVERFLOW
        y = self.bus.read_int16_data(self.address, self.HMC5883L_DYRA)
        if y == -4096: y = OVERFLOW
        z = self.bus.read_int16_data(self.address, self.HMC5883L_DZRA)
        if z == -4096: z = OVERFLOW

        x*=self._scale
        y*=self._scale
        z*=self._scale

        if offset: (x, y, z) = self.__offset((x,y,z))

        return (x, y, z)

    def __str__(self):
        (x, y, z) = self.axes()
        return "Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n" \

    def __offset(self, read):
        (x, y, z) = read

        if x < self.x[0]: self.x[0] = x
        if x > self.x[1]: self.x[1] = x

        if y < self.y[0]: self.y[0] = y
        if y > self.y[1]: self.y[1] = y

        if z < self.z[0]: self.z[0] = z
        if z > self.z[1]: self.z[1] = z

        x = x - (self.x[0]+self.x[1])/2
        y = y - (self.y[0]+self.y[1])/2
        z = z - (self.z[0]+self.z[1])/2

        return (x, y, z)


    def get_azimuth(self, offset = -90):
        (x, y, z) = self.axes(offset = True)

        heading = math.atan2(y, x)

        if heading < 0:
            heading += 2*math.pi

        if heading > 2*math.pi:
            heading -= 2*math.pi

        heading = heading * 180/math.pi; 

        heading += offset
        if heading > 360: heading -= 360
        if heading < 0: heading += 360


        return 360-heading

