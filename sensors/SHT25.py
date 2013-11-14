#!/usr/bin/python

import smbus
import time

class sht25(object):
	'Python library for SHT25v01A MLAB module with Sensirion SHT25 i2c humidity and temperature sensor.'
	SHT25_HEATER_ON = 0x04
	SHT25_HEATER_OFF = 0x00
	SHT25_OTP_reload_off = 0x02
	SHT25_RH12_T14 = 0x00 
	SHT25_RH8_T12 = 0x01
	SHT25_RH10_T13 = 0x80
	SHT25_RH11_T11 = 0x81
	SHT25_ADDRESS = 0x80	# SHT25 has only one device address (factory set)

	def soft_reset(self):
	  self.bus.write_byte(self.address, 0xFE);
	  return

	def __init__(self, port=5):
	  self.bus = smbus.SMBus(port)
	  self.address = SHT25_ADDRESS		# SHT25 has only one device address (factory set)
	  self.soft_reset();

	def setup( setup_reg ):  # writes to status register and returns its value
	  reg=self.bus.read_byte(self.address, 0xE7);    # Read status actual status register
	  reg = (reg & 0x3A) | setup_reg;    # modify actual register status
	  self.bus.i2c_write_bloks(self.address, (0xE6, reg) ); # write new status register
	  reg=self.bus.read_byte(self.address, 0xE7);    # Read status actual status register for check purposes
	  return (reg);

	def get_temp():
	   self.bus.write_byte(self.address, 0xE3); # start temperature measurement
	   time.sleep(0.1)
	   
	   MSB=self.bus.read_byte(self.address)
	   LSB=self.bus.read_byte(self.address)
	   Check=self.bus.read_byte(self.address)
	      
	   LSB = LSB >> 2; # trow out status bits

	   data = (( MSB << 8) + (LSB << 4));
	   return(-46.85 + 175.72*(float(data)/0xFFFF));


	def get_hum():
	   self.bus.write_byte(self.address, 0xE5); # start humidity measurement
	   time.sleep(0.1)

	   MSB=self.bus.read_byte(self.address)
	   LSB=self.bus.read_byte(self.address)
	   Check=self.bus.read_byte(self.address)

	   LSB = LSB >> 2; # trow out status bits

	   data = ((MSB << 8) + (LSB << 4) );
	   return( -6.0 + 125.0*(float(data) /  0xFFFF));



