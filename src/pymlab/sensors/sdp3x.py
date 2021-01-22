#!/usr/bin/python

# Python driver for MLAB SDP3x diff pressure sensor

import math
import time
import sys
import logging
import time

from pymlab.sensors import Device

import struct

LOGGER = logging.getLogger(__name__)


class SDP3x(Device):
    """
    Driver for the SDP3x diff pressure sensor.
    """

    def __init__(self, parent = None, address = 0x21, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def initialize(self):
        self.reset()
        self.bus.write_byte(self.address, 0x00) # SDP3x device wakeup
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x36, 0x7C)
        self.bus.write_byte_data(self.address, 0xE1, 0x02)
        p_id = self.bus.read_i2c_block(self.address, 18)
        p_num = ((p_id[0] << 24) | (p_id[1] << 16) | (p_id[3] << 8) | p_id[4])

        if (p_num == 0x03010101):
            sensor = "SDP31"
        elif (p_num == 0x03010201):
            sensor = "SDP32"
        elif (p_num == 0x03010384):
            sensor = "SDP33"
        else:
            sensor = "unknown"
        print("ID: %s - sensor: %s" % (hex(p_num), sensor))

        self.bus.write_byte_data(self.address, 0x36, 0x15) 

    def reset(self):
        self.bus.write_byte(self.address, 0x00) # SDP3x device wakeup
        time.sleep(0.1)
        self.bus.write_byte(0x00, 0x06) # SDP3x device soft reset
        time.sleep(0.1)


    def readData(self):
        raw_data = self.bus.read_i2c_block(self.address, 9)
        press_data = raw_data[0]<<8 | raw_data[1]
        temp_data = raw_data[3]<<8 | raw_data[4]

        if (press_data > 0x7fff):
            press_data -= 65536
        
        if (temp_data > 0x7fff):
            temp_data -= 65536
        
        dpsf = float(raw_data[6]<<8 | raw_data[7])
        
        if(dpsf == 0):
            press_data = 0.0
        else:
            press_data /= dpsf

        temp_data /= 200

        return press_data, temp_data