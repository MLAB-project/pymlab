#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor
#
# print "LTS01A status",  bin(get_config(I2C_bus_number, LTS01A_address))
# Return statust register value
# print "LTS01A temp", get_temp(I2C_bus_number, LTS01A_address)
# return temperature.


import struct
import logging

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class LTS01(Device):
    """
    Example:

    .. code-block:: python
    
        # Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

    """
    
    FAULTS = {
        1: [0b00],
        2: [0b01],
        4: [0b10],
        6: [0b11],
    }

    def __init__(self, parent = None, address = 0x48, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions 
        self.Reg_temp = 0x00
        self.Reg_conf = 0x01
        self.Reg_Thys = 0x02
        self.Reg_Tos = 0x03

## config parameters
        self.SHUTDOWN = (1 << 0)
        self.INTERRUPT_Mode = (1 << 1)
        self.COMPARATOR_Mode = (0 << 1)
        self.OS_POLARITY_1 = (1 << 2)
        self.OS_POLARITY_0 = (0 << 2)
#        self.FQ_num = (int(self.FAULTS[fault_queue]) << 3)
        self.FORMAT_2complement = (0 << 5)
        self.FORMAT_extended = (1 << 5)
        self.Timeout_on = (0 << 6)
        self.Timeout_off = (1 << 6)

    def initialize(self):
        setup = 0x00
        self.bus.write_byte_data(self.address, self.Reg_conf, setup)
        LOGGER.debug("LTS sensor initialized. ",)
        return self.bus.read_byte_data(self.address,0x01);


    def get_temp(self):
#        self.bus.write_byte(self.address,0x00)
        temp = self.bus.read_int16_data(self.address, self.Reg_temp) / 256.0 
        #temperature calculation register_value * 0.00390625; (Sensor is a big-endian but SMBus is little-endian by default)
        return temp


