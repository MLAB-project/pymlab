#!/usr/bin/python

import smbus

class i2chub(object):
	'Python library for I2CHUB02A MLAB module with TCA9548A i2c bus expander. '

	ch0 = 0b00000001
	ch1 = 0b00000010
	ch2 = 0b00000100
	ch3 = 0b00001000
	ch4 = 0b00010000
	ch5 = 0b00100000
	ch6 = 0b01000000
	ch7 = 0b10000000

	def __init__(self, bus_number=5, address=0x70):
	  self.bus = smbus.SMBus(bus_number)
	  self.address = address


	def setup(self,i2c_channel_setup):
	  self.bus.write_byte(self.address, i2c_channel_setup);
	  return -1;

	def status(self):
	  return self.bus.read_byte(self.address);



