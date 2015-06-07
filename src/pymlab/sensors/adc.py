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
    def readTemp(self, vref):           
        self.bus.write_byte(self.address, 0x80)             # switch to internal thermometer
        time.sleep(1)
        value = self.bus.read_i2c_block(self.address, 4)
        time.sleep(1)
        self.bus.write_byte(self.address, 0x00)             # switch to external input   
        time.sleep(1)
        return value


    # reading ADC after conversion and start new conversion
    def readADC(self):           
        return (self.bus.read_i2c_block(self.address, 4))

   


