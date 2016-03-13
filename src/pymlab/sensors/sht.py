#!/usr/bin/python

#import smbus
import time

from pymlab.sensors import Device


#TODO: Implement output data checksum checking 

class SHT25(Device):
    'Python library for SHT25v01A MLAB module with Sensirion SHT25 i2c humidity and temperature sensor.'

    def __init__(self, parent = None, address = 0x40, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.SHT25_HEATER_ON = 0x04
        self.SHT25_HEATER_OFF = 0x00
        self.SHT25_OTP_reload_off = 0x02
        self.SHT25_RH12_T14 = 0x00 
        self.SHT25_RH8_T12 = 0x01
        self.SHT25_RH10_T13 = 0x80
        self.SHT25_RH11_T11 = 0x81
        #self.address = 0x40    # SHT25 has only one device address (factory set)

        self.TRIG_T_HOLD = 0b11100011
        self.TRIG_RH_HOLD = 0b11100101
        self.TRIG_T_noHOLD = 0b11110011
        self.TRIG_RH_noHOLD = 0b11110101
        self.WRITE_USR_REG = 0b11100110
        self.READ_USR_REG = 0b11100111
        self.SOFT_RESET = 0b11111110

    def soft_reset(self):
        self.bus.write_byte(self.address, self.SOFT_RESET);
        return

    def setup(self, setup_reg ):  # writes to status register and returns its value
        reg=self.bus.read_byte_data(self.address, self.READ_USR_REG);    # Read status actual status register
        reg = (reg & 0x3A) | setup_reg;    # modify actual register status leave reserved bits without modification
        self.bus.write_byte_data(self.address, self.WRITE_USR_REG, reg); # write new status register
        return self.bus.read_byte_data(self.address, self.READ_USR_REG);    # Return status actual status register for check purposes

    def get_temp(self):
        self.bus.write_byte(self.address, self.TRIG_T_noHOLD); # start temperature measurement
        time.sleep(0.1)

        data = self.bus.read_i2c_block(self.address, 2)
        value = data[0]<<8 | data[1]
        value &= ~0b11    # trow out status bits
        return(-46.85 + 175.72*(value/65536.0))

    def get_hum(self):
        """
        The physical value RH given above corresponds to the
        relative humidity above liquid water according to World
        Meteorological Organization (WMO)
        """
        self.bus.write_byte(self.address, self.TRIG_RH_noHOLD); # start humidity measurement
        time.sleep(0.1)

        data = self.bus.read_i2c_block(self.address, 2)
        value = data[0]<<8 | data[1]
        value &= ~0b11    # trow out status bits
        humidity = (-6.0 + 125.0*(value/65536.0))
        
        if humidity > 100.0:
            return 100.0
        elif humidity < 0.0:
            return 0.0
        else: 
            return humidity

class SHT31(Device):
    'Python library for SHT31v01A MLAB module with Sensirion SHT31 i2c humidity and temperature sensor.'

    def __init__(self, parent = None, address = 0x44, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.SOFT_RESET = 0x30a2
        self.STATUS_REG = 0x30a2

    def soft_reset(self):
        self.bus.write_word_data(self.address, self.SOFT_RESET);
        return

    def get_status(self):
        self.bus.write_word_data(self.address, self.SOFT_RESET);

    def setup(self, setup_reg ):  # writes to status register and returns its value
        reg=self.bus.read_byte_data(self.address, self.READ_USR_REG);    # Read status actual status register
        reg = (reg & 0x3A) | setup_reg;    # modify actual register status leave reserved bits without modification
        self.bus.write_byte_data(self.address, self.WRITE_USR_REG, reg); # write new status register
        return self.bus.read_byte_data(self.address, self.READ_USR_REG);    # Return status actual status register for check purposes

    def get_temp(self):
        self.bus.write_byte(self.address, self.TRIG_T_noHOLD); # start temperature measurement
        time.sleep(0.1)

        data = self.bus.read_int16(self.address)
        data &= ~0b11    # trow out status bits
        return(-46.85 + 175.72*(data/65536.0))

    def get_hum(self):
        """
The physical value RH given above corresponds to the
relative humidity above liquid water according to World
Meteorological Organization (WMO)
        """
        self.bus.write_byte(self.address, self.TRIG_RH_noHOLD); # start humidity measurement
        time.sleep(0.1)

        data = self.bus.read_uint16(self.address)
        data &= ~0b11    # trow out status bits
        humidity = (-6.0 + 125.0*(data/65536.0))
        if humidity > 100.0:
            return 100.0
        elif humidity < 0.0:
            return 0.0
        else: 
            return humidity


def main():
    print __doc__


if __name__ == "__main__":
    main()
