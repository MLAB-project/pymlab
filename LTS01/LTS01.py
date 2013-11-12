#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor
#
# print "LTS01A status",  bin(get_config(I2C_bus_number, LTS01A_address))
# Return statust register value
# print "LTS01A temp", get_temp(I2C_bus_number, LTS01A_address)
# return temperature.

import smbus
import struct

LTS01A_address = 0x48

INTERRUPT_Mode = 0b00000010
COMPARATOR_Mode = 0b00000000

def get_config(bus_number, address):
  bus = smbus.SMBus(bus_number);
  return bus.read_byte_data(address,0x01);

def get_temp(bus_number, address):
  bus = smbus.SMBus(bus_number);
  temp = struct.unpack("<h", struct.pack(">H", bus.read_word_data(address,0x00)))[0] / 256.0 
#temperature calculation register_value * 0.00390625; (Sensor is a big-endian but SMBus is little-endian by default)
  return temp


def setup(bus_number, address, setup):
  bus = smbus.SMBus(bus_number);
  bus.write_byte_data(address, setup);
  return -1;


