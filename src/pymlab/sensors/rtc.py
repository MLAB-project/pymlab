#!/usr/bin/python

import struct
import logging
import time
import datetime
import math

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class RTC01(Device):
    FUNCT_MODE_32   =  0b00000000
    FUNCT_MODE_50   =  0b00010000
    FUNCT_MODE_count = 0b00100000
    FUNCT_MODE_test =  0b00110000

    MAX_COUNT = 999999


    def __init__(self, parent = None, address = 0x50, possible_adresses = [0x50, 0x51], **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions
        self.CONTROL_STATUS = 0x00

    def initialize(self):
        self.last_reset = time.time()

        LOGGER.debug("RTC01 sensor initialized. ",)
        return self.bus.read_byte_data(self.address,0x01);

    def get_status(self):
        status = self.bus.read_byte_data(self.address, self.CONTROL_STATUS)
        return status

    def set_config(self, config):
        self.bus.write_byte_data(self.address, self.CONTROL_STATUS, config)
        return config

    def set_datetime(self, dt = None):
        if not dt:
            dt = datetime.datetime.utcnow()
        # TODO

    def get_datetime(self):
        for reg in xrange(1,6):
            print (hex(self.bus.read_byte_data(self.address, reg)))

        #TODO
    def get_integration_time(self):
        return time.time()-self.last_reset

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

        return int((a&0x0f)*1 + ((a&0xf0)>>4)*10 + (b&0x0f)*100 + ((b&0xf0)>>4)*1000+ (c&0x0f)*10000 + ((c&0xf0)>>4)*1000000)

    def get_speed(self, **kwargs):
        diameter = kwargs.get('diameter', 1)
        reset = kwargs.get('reset', 0)
        time_reset = kwargs.get('time_reset', 60)

        if time.time() - self.last_reset > time_reset:
            self.reset_counter()

        freq = self.get_frequency()
        spd = math.pi*diameter/1000*freq
        #if reset:
        #    self.reset_counter()
        return spd