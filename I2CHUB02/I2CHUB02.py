#!/usr/bin/python

# Python library for I2CHUB02A MLAB module with TCA9548A i2c bus expander. 

import smbus


#I2CHUB_address = 0x70
#I2CHUB_bus_number = 6

ch0 = 0b00000001
ch1 = 0b00000010
ch2 = 0b00000100
ch3 = 0b00001000
ch4 = 0b00010000
ch5 = 0b00100000
ch6 = 0b01000000
ch7 = 0b10000000


def setup(I2CHUB_bus_number, I2CHUB_address, i2c_channel_setup):
  bus = smbus.SMBus(I2CHUB_bus_number);
  bus.write_byte(I2CHUB_address, i2c_channel_setup);
  return -1;

def get_status(I2CHUB_bus_number, I2CHUB_address):
  bus = smbus.SMBus(I2CHUB_bus_number);
  return bus.read_byte(I2CHUB_address);



