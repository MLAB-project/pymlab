#!/usr/bin/python

# Python driver for MLAB I2CADC01 module

import math
import time
import sys
import logging
import time

from pymlab.sensors import Device

import struct

LOGGER = logging.getLogger(__name__)


class I2CADC01(Device):
 
    def __init__(self, parent = None, address = 0x24, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    # reading internal temperature
    def readTemp(self):           
        self.bus.write_byte(self.address, 0x08)             # switch to internal thermometer, start conversion
        time.sleep(0.2)                                     # wait for conversion
        value = self.bus.read_i2c_block(self.address, 4)    # read converted value
        time.sleep(0.2)                                     # wait for dummy conversion
        v = value[0]<<24 | value[1]<<16 | value[2]<<8 | value[3]
        v ^= 0x80000000
        if (value[0] & 0x80)==0:
            v = v - 0xFFFFFFff 
        voltage = float(v)
        voltage = voltage * 1.225 / (2147483648.0)          # calculate voltage against vref and 24bit
        temperature = (voltage / 0.0014) - 273              # calculate temperature
        return temperature


    # reading ADC after conversion and start new conversion
    def readADC(self):           
        self.bus.write_byte(self.address, 0x00)             # switch to external input, start conversion 
        time.sleep(0.2)                                     # wait for conversion
        value = self.bus.read_i2c_block(self.address, 4)    # read converted value
        time.sleep(0.2)                                     # wait for dummy conversion
        v = value[0]<<24 | value[1]<<16 | value[2]<<8 | value[3]
        v ^= 0x80000000
        if (value[0] & 0x80)==0:
            v = v - 0xFFFFFFff 
        voltage = float(v)
        voltage = voltage * 1.225 / (2147483648.0)          # calculate voltage against vref and 24bit
        return voltage

   


