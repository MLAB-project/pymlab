#!/usr/bin/python

#import smbus
import time
import sys
import datetime
import struct
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

        data = self.bus.read_i2c_block(self.address, 2) # Sensirion digital sensors are pure I2C devices, therefore clear I2C trasfers must be used instead of SMBus trasfers.

        value = data[0]<<8 | data[1]
        value &= ~0b11    # trow out status bits

        return(-46.85 + 175.72/65536.0*value)

    def get_hum(self, raw = False):
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

        if raw:                 # raw sensor output, useful for getting an idea of sensor failure status
            return humidity

        else:

            if humidity > 100.0:        # limit values to relevant physical variable (values out of that limit is sensor error state and are dependent on specific sensor piece)
                return 100.0
            elif humidity < 0.0:
                return 0.0
            else:
                return humidity

class SHT31(Device):
    'Python library for SHT31v01A MLAB module with Sensirion SHT31 i2c humidity and temperature sensor.'

    def __init__(self, parent = None, address = 0x44, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.temperature = None
        self.humidity = None


        self.SOFT_RESET = [0x30, 0xA2]
        self.STATUS_REG = [0xF3, 0x2D]
        self.MEASURE_H_CLKSD = [0x24, 0x00]
        self.READ_PERIODIC = [0xE0, 0x00]
        self.PERIODIC_MEAS_1MPS_M = [0x21, 0x26]
        self.RESET = [0x30, 0xA2]
        self.CLEAR_STATUS = [0x30, 0x41]

        self.selected_mode = self.PERIODIC_MEAS_1MPS_M
        #self.soft_reset()

    def reset(self):
        #self.bus.write_i2c_block(self.address, self.SOFT_RESET);
        # Do sw reset on start
        #time.sleep(1)
        self.bus.write_byte(self.address, 6)
        time.sleep(0.5)
        self.initialize()

    def initialize(self):
        print("Configure")

        self.bus.write_byte_data(self.address, self.CLEAR_STATUS[0], self.CLEAR_STATUS[1])
        time.sleep(0.2)
        self.bus.write_i2c_block_data(self.address, 0xE1, [0x1F, 0xFF, 0xFF, self.calc_checksum([0xff, 0xff])])
        time.sleep(0.2)
        self.bus.write_i2c_block_data(self.address, 0xE1, [0x02, 0x00, 0x00, self.calc_checksum([0x00, 0x00])])
        time.sleep(0.2)
        self.bus.write_i2c_block_data(self.address, 0x61, [0x1D, 0xFF, 0xFF, self.calc_checksum([0xff, 0xff])])
        time.sleep(0.2)
        self.bus.write_i2c_block_data(self.address, 0x61, [0x00, 0x00, 0x00, self.calc_checksum([0x00, 0x00])])

        self.bus.write_byte_data(self.address, self.selected_mode[0], self.selected_mode[1])
        time.sleep(2)


    def get_status(self):
        self.bus.write_i2c_block_data(self.address, self.STATUS_REG[0], self.STATUS_REG[1:])
        status = self.bus.read_i2c_block_data(self.address, 0, 3)
        #print([format(x, '08b') for x in status])
        st = status[1] | (status[0] << 8)
        bits_values = dict([('Invalid_checksum', bool(st & 1<<0)),
                    ('Invalid_command', bool(st & 1<<1)),
                    ('System_reset', bool(st & 1<<4)),
                    ('T_alert', bool(st & 1<<10)),
                    ('RH_alert', bool(st & 1<<11 )),
                    ('Heater', bool(st & 1<<13)),
                    ('Alert_pending', bool(st & 1<<15)),
                    ('Checksum', status[2]) ])
        return bits_values

    def get_periodic_measurement(self):
        print(self.get_status())

        self.bus.write_byte_data(self.address, self.READ_PERIODIC[0], self.READ_PERIODIC[1])
        time.sleep(0.2)
        data = self.bus.read_i2c_block_data(self.address, 0, 6)

        temp_data = data[0]<<8 | data[1]
        hum_data = data[3]<<8 | data[4]

        self.humidity = 100.0*(hum_data/65535.0)
        self.temperature = -45.0 + 175.0*(temp_data/65535.0)
        self.updated = datetime.datetime.now()

        #self.bus.write_byte_data(self.address, self.CLEAR_STATUS[0], self.CLEAR_STATUS[1])


        return(self.temperature, self.humidity)


    def get_TempHum(self):
        self.bus.write_i2c_block_data(self.address, self.MEASURE_H_CLKSD[0], self.MEASURE_H_CLKSD[1:]); # start temperature and humidity measurement
        time.sleep(0.05)

        data = self.bus.read_i2c_block_data(self.address, 0x00, 6)

        temp_data = data[0]<<8 | data[1]
        hum_data = data[3]<<8 | data[4]

        humidity = 100.0*(hum_data/65535.0)
        temperature = -45.0 + 175.0*(temp_data/65535.0)

        return temperature, humidity

    def get_temp(self): #TODO: cist mene i2c bloku ...
        self.bus.write_i2c_block(self.address, self.MEASURE_H_CLKSD); # start temperature and humidity measurement
        time.sleep(0.05)

        data = self.bus.read_i2c_block(self.address, 6)

        temp_data = data[0]<<8 | data[1]
        temperature = -45.0 + 175.0*(temp_data/65535.0)

        return temperature

    def get_humi(self): #TODO: cist mene i2c bloku ...
        self.bus.write_i2c_block(self.address, self.MEASURE_H_CLKSD); # start temperature and humidity measurement
        time.sleep(0.05)

        data = self.bus.read_i2c_block(self.address, 6)

        hum_data = data[3]<<8 | data[4]
        humidity = 100.0*(hum_data/65535.0)

        return humidity


    @staticmethod
    def _calculate_checksum(value):
        """4.12 Checksum Calculation from an unsigned short input"""
        # CRC
        polynomial = 0x131  # //P(x)=x^8+x^5+x^4+1 = 100110001
        crc = 0xFF

        # calculates 8-Bit checksum with given polynomial
        for byteCtr in [ord(x) for x in struct.pack(">H", value)]:
            crc ^= byteCtr
            for bit in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc = (crc << 1)
        return crc

    def calc_checksum(self, data):
        crc = 0xff
        for d in data:
            crc ^= d
            for bit in range(8, 0, -1):
                if bool(crc & 0x80):
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1

        return (crc & 0xff)


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
