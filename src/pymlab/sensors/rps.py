#!/usr/bin/python

# Python library for RPS01A MLAB module with magnetic rotary position I2C Sensor
#
import struct
import logging

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class RPS01(Device):
    """
        MLAB Rotary position sensor I2C driver. 
    """

    def __init__(self, parent = None, address = 0x40, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions 
        self.control = 3
        self.reg_address = 21
        self.zero_position_MSB = 22
        self.zero_position_LSB = 23
        self.AGC = 250
        self.diagnostics = 251
        self.magnitude_MSB = 252
        self.magnitude_LSB = 253
        self.angle_MSB = 254
        self.angle_LSB = 255

    def get_address(self):
        """ 
            Returns sensors I2C address.
        """
        LOGGER.debug("Reading RPS01A sensor's address.",)
        return self.bus.read_byte_data(self.address, self.reg_address)

    def get_agc(self):
        """ 
            Returns sensor's Automatic Gain Control actual value.
        """
        LOGGER.debug("Reading RPS01A sensor's AGC settings",)
        return self.bus.read_byte_data(self.address, self.AGC)

    def get_magnitude(self):
        LSB = self.bus.read_byte_data(self.address, self.magnitude_LSB)
        MSB = self.bus.read_byte_data(self.address, self.magnitude_MSB)
        DATA = (MSB << 6) + LSB
        return DATA

    def get_angle(self):
        LSB = self.bus.read_byte_data(self.address, self.angle_LSB)
        MSB = self.bus.read_byte_data(self.address, self.angle_MSB)
        DATA = (MSB << 6) + LSB
        return DATA


