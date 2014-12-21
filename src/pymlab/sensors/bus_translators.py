#!/usr/bin/python

import smbus
import time

from pymlab.sensors import Device

class I2CSPI(Device):
    'Python library for SC18IS602B chip in I2CSPI MLAB bridge module.'

    def __init__(self, parent = None, address = 0x2E, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.I2CSPI_CONFIGURE = 0x00
        self.I2CSPI_CONFIGURE = 0x00







    def soft_reset(self):
        self.bus.write_byte(self.address, self.SOFT_RESET);
        return


    def setup(self, setup_reg ):  # writes to status register and returns its value
        reg=self.bus.read_byte_data(self.address, self.READ_USR_REG);    # Read status actual status register
        reg = (reg & 0x3A) | setup_reg;    # modify actual register status leave reserved bits without 
        self.bus.write_byte_data(self.address, self.WRITE_USR_REG, reg); # write new status register
        reg=self.bus.read_byte_data(self.address, self.READ_USR_REG);    # Read status actual status register for check purposes
        return (reg);

    def get_temp(self):
        self.bus.write_byte(self.address, self.TRIG_T_noHOLD); # start temperature measurement
        time.sleep(0.1)

        data = self.bus.read_int16(self.address)
        data &= ~0b11    # trow out status bits
        return(-46.85 + 175.72*(data/65536.0));

    def get_hum(self):
        self.bus.write_byte(self.address, self.TRIG_RH_noHOLD); # start humidity measurement
        time.sleep(0.1)

        data = self.bus.read_uint16(self.address)
        data &= ~0b11    # trow out status bits
        return(-6.0 + 125.0*(data/65536.0));


def main():
    print __doc__


if __name__ == "__main__":
    main()
