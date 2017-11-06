#!/usr/bin/python

import struct
import logging
import time

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class RTC01(Device):
    FUNCT_MODE_32   =  0b00000000
    FUNCT_MODE_50   =  0b00010000
    FUNCT_MODE_count = 0b00100000
    FUNCT_MODE_test =  0b00110000


    def __init__(self, parent = None, address = 0x50, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions 
        self.CONTROL_STATUS = 0x00

    def initialize(self):
        self.last_reset = time.time()
        
        #self.bus.write_byte_data(self.address, self.Reg_conf, setup)

        LOGGER.debug("RTC01 sensor initialized. ",)
        return self.bus.read_byte_data(self.address,0x01);

    def get_status(self):
        status = self.bus.read_byte_data(self.address, self.CONTROL_STATUS)
        return status

    def set_config(self, config):
        self.bus.write_byte_data(self.address, self.CONTROL_STATUS, config)
        return config

    def reset_counter(self):
        self.bus.write_byte_data(self.address,0x01,0x00)
        self.bus.write_byte_data(self.address,0x02,0x00)
        self.bus.write_byte_data(self.address,0x03,0x00)
        self.last_reset = time.time()

    def get_frequency(self):
        delta = time.time()-self.last_reset
        count = self.get_count()
        freq = 1.0*(count/delta)
        return freq

    def get_count(self):
        a = self.bus.read_byte_data(self.address, 0x01)
        b = self.bus.read_byte_data(self.address, 0x02)
        c = self.bus.read_byte_data(self.address, 0x03)

        return int((a&0x0f)*1 + ((a&0xf0)>>4)*10 + (b&0x0f)*100 + ((b&0xf0)>>4)*1000)

    def get_temp(self):
#        self.bus.write_byte(self.address,0x00)
        temp = self.bus.read_int16_data(self.address, self.Reg_temp) / 256.0 
        #temperature calculation register_value * 0.00390625; (Sensor is a big-endian but SMBus is little-endian by default)
        return temp


