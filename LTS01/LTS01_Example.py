#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

import smbus
import struct
#import ../I2CHUB02/I2CHUB02
import LTS01

I2C_bus_number = 5
#I2CHUB_address = 0x70

# activate I2CHUB port connected to LTS01A sensor
#I2CHUB02.setup(I2C_bus_number, I2CHUB_address, I2CHUB02.ch0);

LTS01A_address = 0x48

print "LTS01A status",  bin(LTS01.get_config(I2C_bus_number, LTS01A_address))
print "LTS01A temp", LTS01.get_temp(I2C_bus_number, LTS01A_address)
