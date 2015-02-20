#!/usr/bin/python

# Python library for ISL2902001A MLAB module with ISL29020 I2C Light Sensor
#
# print "LTS01A status",  bin(get_config(I2C_bus_number, LTS01A_address))
# Return statust register value
# print "LTS01A temp", get_temp(I2C_bus_number, LTS01A_address)
# return temperature.


import struct
import logging

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class ISL01(Device):
    """

    """

    RANGE = {
        1000: [0b00, 1/1000],
        4000: [0b01, 1/4000],
        16000: [0b10, 1/16000],
        64000: [0b11, 1/64000],
    }

    def __init__(self, parent = None, address = 0x44, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions 
        self.command = 0x00
        self.Data_lsb = 0x01
        self.Data_msb = 0x02

## config parameters
        self.SHUTDOWN = (1 << 7)
        self.continuous_measurement = (1 << 6)
        self.IR_sense = (1 << 5)
        self.VIS_sense = (0 << 5)
        self.clock_INT_16bit = (0b000 << 4)
        self.clock_INT_12bit = (0b001 << 4)
        self.clock_INT_8bit = (0b010 << 4)
        self.clock_INT_4bit = (0b011 << 4)
        self.clock_EXT_ADC = (0b100 << 4)
        self.clock_EXT_Timer = (0b101 << 4)
        self.range_1kLUX = 0b00
        self.range_4kLUX = 0b01
        self.range_16kLUX = 0b10
        self.range_64kLUX = 0b11

    def ADC_sync(self):
        """ 
        Ends the current ADC-integration and starts another. Used only with External Timing Mode.
        """
        self.bus.write_byte_data(self.address, 0xff, 0x01)
        LOGGER.debug("syncing ILS ADC",)
        return


    def get_lux(self):
        LSB = self.bus.read_byte_data(self.address, self.Data_lsb)
        MSB = self.bus.read_byte_data(self.address, self.Data_lsb)
        DATA = (MSB << 8) + LSB
        Ecal = * DATA
        return Ecal


