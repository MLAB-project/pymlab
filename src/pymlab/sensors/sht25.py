#!/usr/bin/python

import smbus
import time

from pymlab.sensors import Device


#TODO: Implement measurement checksum checking 

class SHT25(Device):
	'Python library for SHT25v01A MLAB module with Sensirion SHT25 i2c humidity and temperature sensor.'

	def soft_reset(self):
		self.bus.write_byte(self.address, 0xFE);
		return

	def __init__(self, parent = None, address = 0x40, **kwargs):
		Device.__init__(self, parent, address, **kwargs)

		self.SHT25_HEATER_ON = 0x04
		self.SHT25_HEATER_OFF = 0x00
		self.SHT25_OTP_reload_off = 0x02
		self.SHT25_RH12_T14 = 0x00 
		self.SHT25_RH8_T12 = 0x01
		self.SHT25_RH10_T13 = 0x80
		self.SHT25_RH11_T11 = 0x81
		#self.address = 0x40	# SHT25 has only one device address (factory set)

		#self.bus = smbus.SMBus(port)
		#self.soft_reset();

	def setup(self, setup_reg ):  # writes to status register and returns its value
		reg=self.bus.read_byte_data(self.address, 0xE7);    # Read status actual status register
		reg = (reg & 0x3A) | setup_reg;    # modify actual register status
		self.bus.write_byte_data(self.address, 0xE6, reg); # write new status register
		reg=self.bus.read_byte_data(self.address, 0xE7);    # Read status actual status register for check purposes
		return (reg);

	def get_temp(self):
		self.bus.write_byte(self.address, 0xE3); # start temperature measurement
		time.sleep(0.1)

		MSB=self.bus.read_byte(self.address)
		LSB=self.bus.read_byte(self.address)
		Check=self.bus.read_byte(self.address)

		LSB = LSB >> 2; # trow out status bits

		data = (( MSB << 8) + (LSB << 4));
		return(-46.85 + 175.72*(float(data)/0xFFFF));

	def get_hum(self):
		self.bus.write_byte(self.address, 0xE5); # start humidity measurement
		time.sleep(0.1)

		MSB=self.bus.read_byte(self.address)
		LSB=self.bus.read_byte(self.address)
		Check=self.bus.read_byte(self.address)

		LSB = LSB >> 2; # trow out status bits

		data = ((MSB << 8) + (LSB << 4) );
		return( -6.0 + 125.0*(float(data) /  0xFFFF));


def main():
	print __doc__


if __name__ == "__main__":
	main()
