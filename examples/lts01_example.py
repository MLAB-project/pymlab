#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

import smbus
import struct
#import ../I2CHUB02/I2CHUB02
import lts01
import sys

I2C_bus_number = 8
#I2CHUB_address = 0x70

# activate I2CHUB port connected to LTS01A sensor
#I2CHUB02.setup(I2C_bus_number, I2CHUB_address, I2CHUB02.ch0);

LTS01A_address = 0x48

thermometer = lts01.LTS01(int(sys.argv[1]),LTS01A_address)

print "LTS01A status",  bin(thermometer.config())
print "LTS01A temp", thermometer.temp()
