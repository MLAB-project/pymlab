#!/usr/bin/python

# Python library for SHT25v01A MLAB module with SHT25 i2c humidity and temperature sensor.
#

import smbus
import time

class SHT25:

  SHT25_HEATER_ON = 0x04
  SHT25_HEATER_OFF = 0x00
  SHT25_OTP_reload_off = 0x02
  SHT25_RH12_T14 = 0x00 
  SHT25_RH8_T12 = 0x01
  SHT25_RH10_T13 = 0x80
  SHT25_RH11_T11 = 0x81

  SHT25_ADDR = 0x80

bus_number =5

def soft_reset():
  bus = smbus.SMBus(bus_number);
  bus.write_byte(SHT25_ADDR, 0xFE);
  return

def setup( setup_reg ):  # writes to status register and returns its value
  bus = smbus.SMBus(bus_number);
  reg=bus.read_byte(SHT25_ADDR, 0xE7);    # Read status actual status register
  reg = (reg & 0x3A) | setup_reg;    # modify actual register status
  bus.i2c_write_bloks(SHT25_ADDR, (0xE6, reg) ); # write new status register
  reg=bus.read_byte(SHT25_ADDR, 0xE7);    # Read status actual status register for check purposes
  return (reg);

def get_temp():
   bus = smbus.SMBus(bus_number);
   bus.write_byte(SHT25_ADDR, 0xE3); # start temperature measurement
   time.sleep(0.1)
   
   MSB=bus.read_byte(SHT25_ADDR)
   LSB=bus.read_byte(SHT25_ADDR)
   Check=bus.read_byte(SHT25_ADDR)
      
   LSB = LSB >> 2; # trow out status bits

   data = (( MSB << 8) + (LSB << 4));
   return(-46.85 + 175.72*(float(data)/0xFFFF));


def get_hum():
   bus = smbus.SMBus(bus_number);
   bus.write_byte(SHT25_ADDR, 0xE5); # start humidity measurement
   time.sleep(0.1)

   MSB=bus.read_byte(SHT25_ADDR)
   LSB=bus.read_byte(SHT25_ADDR)
   Check=bus.read_byte(SHT25_ADDR)

   LSB = LSB >> 2; # trow out status bits

   data = ((MSB << 8) + (LSB << 4) );
   return( -6.0 + 125.0*(float(data) /  0xFFFF));



