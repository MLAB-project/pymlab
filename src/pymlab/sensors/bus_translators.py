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

        self.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_LEADING = 0b00 # SPICLK LOW when idle; data clocked in on leading edge (CPOL = 0, CPHA = 0)
        self.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_TRAILING = 0b01 # SPICLK LOW when idle; data clocked in on trailing edge (CPOL = 0, CPHA = 1)
        self.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING = 0b10 # SPICLK HIGH when idle; data clocked in on trailing edge (CPOL = 1, CPHA = 0)
        self.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_LEADING = 0b11 # SPICLK HIGH when idle; data clocked in on leading edge (CPOL = 1, CPHA = 1)

        self.I2CSPI_CLK_1843kHz = 0b00
        self.I2CSPI_CLK_461kHz = 0b01
        self.I2CSPI_CLK_115kHz = 0b10
        self.I2CSPI_CLK_58kHz = 0b11


    def SPI_write(self, chip_select, data):
    'Writes data to SPI device selected by chipselect bit. ' 
        self.write_block_data(self.address, chip_select,  data);
        return

    def SPI_read(self):
    'Reads data from I2CSPII buffer. ' 
        return self.read_block_data(self.address);

    def SPI_config(self,config):
    'Reads data from I2CSPII buffer. ' 
        return self.write_byte_data(self.address, 0x00, config);

    def SPI_clear_INT(self):
    'Reads data from I2CSPII buffer. ' 
        return self.write_byte(self.address, 0x00);



def main():
    print __doc__


if __name__ == "__main__":
    main()
