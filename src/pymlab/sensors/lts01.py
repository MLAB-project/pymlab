#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor
#
# print "LTS01A status",  bin(get_config(I2C_bus_number, LTS01A_address))
# Return statust register value
# print "LTS01A temp", get_temp(I2C_bus_number, LTS01A_address)
# return temperature.


import struct

from pymlab.sensors import Device, register


@register("lts01")
class LTS01(Device):
	"""
	Example:

	.. code-block:: python
	
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

	"""
	
	def __init__(self, parent = None, address = 0x48, **kwargs):
		Device.__init__(self, parent, address, **kwargs)

		self.INTERRUPT_Mode = 0b00000010
		self.COMPARATOR_Mode = 0b00000000
	
	def config(self):
		return self.bus.read_byte_data(self.address,0x01)

	def temp(self):
		temp = struct.unpack("<h", struct.pack(">H", self.bus.read_word_data(self.address,0x00)))[0] / 256.0 
		#temperature calculation register_value * 0.00390625; (Sensor is a big-endian but SMBus is little-endian by default)
		return temp

	def setup(self):
		self.bus.write_byte_data(address, setup)
		return -1

