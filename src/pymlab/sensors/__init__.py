#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import smbus

#from pymlab import config
from pymlab.utils import obj_repr


CHANNEL_0 = 0b00000001
CHANNEL_1 = 0b00000010
CHANNEL_2 = 0b00000100
CHANNEL_3 = 0b00001000
CHANNEL_4 = 0b00010000
CHANNEL_5 = 0b00100000
CHANNEL_6 = 0b01000000
CHANNEL_7 = 0b10000000


class Overflow(object):
	def __repr__(self):
		return "OVERFLOW"

	def __str__(self):
		return repr(self)

	def __add__(self, other):
		return self

	def __sub__(self, other):
		return self

	def __mul__(self, other):
		return self


OVERFLOW = Overflow()


class Device(object):
	"""Base class for all MLAB sensors."""	
	
	def __init__(self, parent = None, address = 0x70, **kwargs):
		self.parent  = parent
		self.address = address
		self.channel = kwargs.get("channel", None)

	def __repr__(self):
		return obj_repr(self, address = self.address)

	@property
	def bus(self):
		if isinstance(self.parent, Bus):
			return self.parent
		return self.parent.bus

	def route(self, child = None):
		if child is None:
			path = []
			node = self
			while not isinstance(node, Bus):
				path.insert(0, node)
				node = node.parent
			path.insert(0, node)

			for i in range(len(path) - 1):
				node = path[i]
				child = path[i + 1]
				if not node.route(child):
					return False
			return True
		
		return False

	def write_byte(self, value):
		return self.bus.write_byte(self.address, value)

	def read_byte(self):
		return self.bus.read_byte(self.address)


class SimpleBus(Device):
	def __init__(self, parent, children = None, **kwargs):
		Device.__init__(self, parent, None, **kwargs)

		self.children = {}

		children = children or []
		for child in children:
			self.children[child.address] = child

	def __iter__(self):
		return self.itervalues()

	def __getitem__(self, key):
		return self.children[key]

	def route(self, child):
		if child.address not in self.children:
			return False
		return True

	def add_child(self, device):
		if device.address in self.children:
			raise Exception("")
		self.children[device.address] = device
		device.parent = self


class Bus(SimpleBus):
	def __init__(self, port = 5):
		SimpleBus.__init__(self, None)

		self.bus = smbus.SMBus(port)
	
	def __repr__(self):
		return obj_repr(self, port = self.port)


def main():
	print __doc__


if __name__ == "__main__":
	main()
