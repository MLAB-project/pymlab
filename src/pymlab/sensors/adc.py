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
             1: 0b00000,
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

class BRIDGEADC01(Device):
    """
    Driver for the AD7730/AD7730L bridge ADC device.
    """

    def __init__(self, parent = None, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        #AD7730 register address
        self.AD7730_COMM_REG            =0b000
        self.AD7730_STATUS_REG          =0b000
        self.AD7730_DATA_REG            =0b001
        self.AD7730_MODE_REG            =0b010
        self.AD7730_FILTER_REG          =0b011
        self.AD7730_DAC_REG             =0b100
        self.AD7730_OFFSET_REG          =0b101
        self.AD7730_GAIN_REG            =0b110
        self.AD7730_TEST_REG            =0b111      # do not change state of this register

    def reset(self):
        spi.SPI_write(spi.I2CSPI_SS0, [0xFF])       # wrinting least 32 serial clock with 1 at data input resets the device.
        spi.SPI_write(spi.I2CSPI_SS0, [0xFF])
        spi.SPI_write(spi.I2CSPI_SS0, [0xFF])
        spi.SPI_write(spi.I2CSPI_SS0, [0xFF])

    def single_write(self, register, value):
        comm_reg = 0b00000 << 3 + register
        spi.SPI_write(spi.I2CSPI_SS0, [comm_reg])
        spi.SPI_write(spi.I2CSPI_SS0, [value])

    def single_read(self, register, value):
        comm_reg = 0b00010 << 3 + register

        if register == self.AD7730_STATUS_REG:
            bytes_num = 1
        elif register == self.AD7730_DATA_REG:
            bytes_num = 2
        elif register == self.AD7730_MODE_REG:
            bytes_num = 2
        elif register == self.AD7730_FILTER_REG:
            bytes_num = 3
        elif register == self.AD7730_DAC_REG:
            bytes_num = 1
        elif register == self.AD7730_OFFSET_REG:
            bytes_num = 3
        elif register == self.AD7730_GAIN_REG:
            bytes_num = 3
        elif register == self.AD7730_TEST_REG:
            bytes_num = 3

        spi.SPI_write(spi.I2CSPI_SS0, [comm_reg])

        return spi.SPI_write(spi.I2CSPI_SS0, bytes_num)


class VCAI2C01(Device):
    """
    Current loop transducer measurement module.
    """
    def __init__(self, parent = None, address = 0x68 , gain = 1, sample_rate = 240, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.rate = sample_rate
        self.gain = gain
        self.address = address

    def initialize(self):
        self.setADC(sample_rate = self.rate)

    def setADC(self, channel = 1, gain = 1, continuous = True, sample_rate = 240 ):
        CHANNEL_CONFIG = {
            1: 0b0000000,
            2: 0b0100000,
            3: 0b1000000,
            4: 0b1100000,
        }

        RATE_CONFIG = {
            240:  0b0000,
            60:   0b0100,
            15:   0b1000,
            3.75: 0b1100,
        }

        GAIN_CONFIG = {
            1: 0b00,
            2: 0b01,
            4: 0b10,
            8: 0b11,
        }

        self.rate = sample_rate
        self.gain = gain

        config = int(CHANNEL_CONFIG[channel] + (continuous << 4) + RATE_CONFIG[sample_rate] + GAIN_CONFIG[gain])
        self.bus.write_byte(self.address, config)

    def readADC(self):
        if self.rate == 240:
            data = self.bus.read_i2c_block(self.address, 3)    # read converted value
            value = (data[0] & 0x0F) << 8 | data[1]
            self.config = data[2]

        elif self.rate == 60:
            data = self.bus.read_i2c_block(self.address, 3)    # read converted value
            value = (data[0] & 0x3F) << 8 | data[1]
            self.config = data[2]

        elif self.rate == 15:
            data = self.bus.read_i2c_block(self.address, 3)    # read converted value
            value =  data[0] << 8 | data[1]
            self.config = data[2]

        elif self.rate == 3.75:
            data = self.bus.read_i2c_block(self.address, 4)    # read converted value
            value = (data[0] & 0x03) << 16 | data[1] << 8 | data[2]
            self.config = data[3]

        return value

    def readVoltage(self):

        value = self.readADC()

        if self.rate == 240:
            value = float(value)/self.gain*3/550

        elif self.rate == 60:
            value = float(value)/self.gain*3/2200

        elif self.rate == 15:
            value = float(value)/self.gain*3/8800

        elif self.rate == 3.75:
            value = float(value)/self.gain*3/35200

        return value

    def readCurrent(self):

        value = float(self.readVoltage())*1000/249

        return value
