#!/usr/bin/python

#import smbus
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

        self.SS0_BIDIRECT   = 0b00
        self.SS0_PUSHPULL   = 0b01
        self.SS0_INPUT      = 0b10
        self.SS0_OPENDRAIN  = 0b11
        self.SS1_BIDIRECT   = 0b0000
        self.SS1_PUSHPULL   = 0b0100
        self.SS1_INPUT      = 0b1000
        self.SS1_OPENDRAIN  = 0b1100
        self.SS2_BIDIRECT   = 0b000000
        self.SS2_PUSHPULL   = 0b010000
        self.SS2_INPUT      = 0b100000
        self.SS2_OPENDRAIN  = 0b110000
        self.SS3_BIDIRECT   = 0b00000000
        self.SS3_PUSHPULL   = 0b01000000
        self.SS3_INPUT      = 0b10000000
        self.SS3_OPENDRAIN  = 0b11000000


        self.I2CSPI_MSB_FIRST = 0b0
        self.I2CSPI_LSB_FIRST = 0b100000

        self.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_LEADING = 0b0000 # SPICLK LOW when idle; data clocked in on leading edge (CPOL = 0, CPHA = 0)
        self.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_TRAILING = 0b0100 # SPICLK LOW when idle; data clocked in on trailing edge (CPOL = 0, CPHA = 1)
        self.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING = 0b1000 # SPICLK HIGH when idle; data clocked in on trailing edge (CPOL = 1, CPHA = 0)
        self.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_LEADING = 0b1100 # SPICLK HIGH when idle; data clocked in on leading edge (CPOL = 1, CPHA = 1)

        self.I2CSPI_CLK_1843kHz = 0b00
        self.I2CSPI_CLK_461kHz = 0b01
        self.I2CSPI_CLK_115kHz = 0b10
        self.I2CSPI_CLK_58kHz = 0b11


    def SPI_write_byte(self, chip_select, data):
        'Writes a data to a SPI device selected by chipselect bit. '
        self.bus.write_byte_data(self.address, chip_select, data)

    def SPI_read_byte(self):
        'Reads a data from I2CSPI buffer. '
        #return self.bus.read_i2c_block_data(self.address, 0xF1) # Clear interrupt and read data
        return self.bus.read_byte(self.address)

    def SPI_write(self, chip_select, data):
        'Writes data to SPI device selected by chipselect bit. '
        dat = list(data)
        dat.insert(0, chip_select)
        return self.bus.write_i2c_block(self.address, dat);  # up to 8 bytes may be written.

    def SPI_read(self, length):
        'Reads data from I2CSPI buffer. '
        return self.bus.read_i2c_block(self.address, length)

    def SPI_config(self,config):
        'Configure SPI interface parameters.'
        self.bus.write_byte_data(self.address, 0xF0, config)
        return self.bus.read_byte_data(self.address, 0xF0)

    def SPI_clear_INT(self):
        'Clears an interrupt at INT pin generated after the SPI transmission has been completed. '
        return self.bus.write_byte(self.address, 0xF1)

    def Idle_mode(self):
        'Turns the bridge to low power idle mode.'
        return self.bus.write_byte(self.address, 0xF2)

    def GPIO_write(self, value):
        'Write data to GPIO enabled slave-selects pins.'
        return self.bus.write_byte_data(self.address, 0xF4, value)

    def GPIO_read(self):
        'Reads logic state on GPIO enabled slave-selects pins.'
        self.bus.write_byte_data(self.address, 0xF5, 0x0f)
        status = self.bus.read_byte(self.address)
        bits_values = dict([('SS0',status & 0x01 == 0x01),('SS1',status & 0x02 == 0x02),('SS2',status & 0x04 == 0x04),('SS3',status & 0x08 == 0x08)])
        return bits_values

    def GPIO_config(self, gpio_enable, gpio_config):
        'Enable or disable slave-select pins as gpio.'
        self.bus.write_byte_data(self.address, 0xF6, gpio_enable)
        self.bus.write_byte_data(self.address, 0xF7, gpio_config)
        return


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
