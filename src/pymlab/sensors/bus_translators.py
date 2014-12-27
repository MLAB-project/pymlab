#!/usr/bin/python

import smbus
import time

from pymlab.sensors import Device

class I2CSPI(Device):
    'Python library for SC18IS602B chip in I2CSPI MLAB bridge module.'

    def __init__(self, parent = None, address = 0x2E, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.I2CSPI_SS0 = 0b0001
        self.I2CSPI_SS1 = 0b0010
        self.I2CSPI_SS2 = 0b0100
        self.I2CSPI_SS3 = 0b1000

        self.I2CSPI_MSB_FIRST = 0b0
        self.I2CSPI_LSB_FIRST = 0b10000

        self.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_LEADING = 0b0000 # SPICLK LOW when idle; data clocked in on leading edge (CPOL = 0, CPHA = 0)
        self.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_TRAILING = 0b0100 # SPICLK LOW when idle; data clocked in on trailing edge (CPOL = 0, CPHA = 1)
        self.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING = 0b1000 # SPICLK HIGH when idle; data clocked in on trailing edge (CPOL = 1, CPHA = 0)
        self.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_LEADING = 0b1100 # SPICLK HIGH when idle; data clocked in on leading edge (CPOL = 1, CPHA = 1)

        self.I2CSPI_CLK_1843kHz = 0b00
        self.I2CSPI_CLK_461kHz = 0b01
        self.I2CSPI_CLK_115kHz = 0b10
        self.I2CSPI_CLK_58kHz = 0b11


    def SPI_write(self, chip_select, data):
        'Writes data to SPI device selected by chipselect bit. ' 
#        return self.bus.write_i2c_block_data(self.address, chip_select,  data);  # up to 200 bytes may be written. 
        return self.bus.write_int16(self.address, chip_select,  data);  # up to 200 bytes may be written. 

    def SPI_read(self):
        'Reads data from I2CSPI buffer. ' 
        return self.bus.read_i2c_block_data(self.address, 0x00)

    def SPI_config(self,config):
        'Configure SPI interface parameters.'
        self.bus.write_byte_data(self.address, 0x00, config)
        return self.bus.read_byte_data(self.address, 0x00)

    def SPI_clear_INT(self):
        'Clears an interrupt at INT pin generated after the SPI trnsmission has been completed. ' 
        return self.bus.write_byte(self.address, 0x01)

    def Idle_mode(self):
        'Turns the bridge to low power idle mode.' 
        return self.bus.write_byte(self.address, 0x02)

    def GPIO_write(self, value):
        'Write data to GPIO enabled slave-selects pins.' 
        return self.bus.write_byte_data(self.address, 0x04, value)

    def GPIO_read(self):
        'Reads logic state on GPIO enabled slave-selects pins.' 
        self.bus.write_byte_data(self.address, 0x05, 0x0f)
        return self.bus.read_byte(self.address)

    def GPIO_config(self, gpio_enable, gpio_config):
        'Enable or disable slave-select pins as gpio.' 
        self.bus.write_byte_data(self.address, 0x06, gpio_enable)
        self.bus.write_byte_data(self.address, 0x07, gpio_config)
        return 


def main():
    print __doc__


if __name__ == "__main__":
    main()
