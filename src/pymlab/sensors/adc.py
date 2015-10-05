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
    """
    Driver for the LTC2485 Linear Technology I2C ADC device. 
    """

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

class LTC2453(Device):
    """
    Driver for the LTC2453 Linear Technology I2C ADC device. 
    """
    def __init__(self, parent = None, address = 0x14, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def readADC(self):           
        value = self.bus.read_i2c_block(self.address, 2)    # read converted value
        v = value[0]<<8 | value[1] 
        v = v - 0x8000
        return v

class LTC2487(Device):
    """
    Driver for the LTC2487 Linear Technology I2C ADC device. 
    """
    def __init__(self, parent = None, address = 0x14, configuration = [0b10111000,0b10011000], **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.config = configuration

    def initialize(self):
        self.bus.write_i2c_block(self.address, self.config)

    def setADC(self, channel = 0 ):           
        CHANNEL_CONFIG = {
            01: 0b00000,
            23: 0b00001,
            10: 0b01000,
            32: 0b01001,
            0: 0b10000,
            1: 0b11000,
            2: 0b10001,
            3: 0b11000,
        }

        self.config[0] = 0b10100000 + CHANNEL_CONFIG[channel]
        self.bus.write_i2c_block(self.address, self.config)

    def readADC(self):           
        data = self.bus.read_i2c_block(self.address, 3)    # read converted value
        value = (data[0] & 0x3F)<<10 | data[1] << 2 | data[2] >> 6
        if (data[0] >> 6) == 0b11:
            value = "OVERFLOW"
        elif (data[0] >> 6) == 0b10:
            value
        elif (data[0] >> 6) == 0b01:
            value = value * -1
        elif (data[0] >> 6) == 0b00:
            value = "UNDERFLOW"
        
        return value

