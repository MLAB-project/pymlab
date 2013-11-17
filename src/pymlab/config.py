#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.config module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import sys
import json

from utils import obj_repr, PrettyPrinter


class Node(object):
	def __init__(self, address, name = None):
		self.address = address
		self.name    = name

	def __repr__(self):
		return obj_repr(self, self.address, self.name)

	def __pprint__(self, printer, level = 0):
		printer.write("%s  %d  %s" % (type(self).__name__, self.address, self.name, ))


class Multiplexer(Node):
	CHANNEL0 = 0b00000001
	CHANNEL1 = 0b00000010
	CHANNEL2 = 0b00000100
	CHANNEL3 = 0b00001000
	CHANNEL4 = 0b00010000
	CHANNEL5 = 0b00100000
	CHANNEL6 = 0b01000000
	CHANNEL7 = 0b10000000

	def __init__(self, address, name = None, children = None):
		Node.__init__(self, address, name)
		self.children = dict(children or {})

	def __repr__(self):
		return obj_repr(self, self.address, self.name, self.children)

	def __pprint__(self, printer, level = 0):
		printer.writeln("%s  %d  %s" % (type(self).__name__, self.address, self.name, ))
		printer.indent()
		for channel, child in self.children.iteritems():
			printer.write("%d:  " % (channel, ))
			printer.format_inner(child, level + 1)
			printer.writeln()
		printer.unindent()


class Sensor(Node):
	pass


class Config(object):
	"""
	Example:

	>>> root = mult(
	... 	address = 0x70,
	... 	name    = "Multiplexer 1",
	... 	children = {
	... 		0x01: mult(
	... 			address = 0x72,
	... 			name    = "Multiplexer 2",
	... 			children = {
	... 				0x01: sens(
	... 					address = 0x68,
	... 					name    = "Sensor 2",
	... 				),
	... 			},
	... 		),
	... 		0x03: sens(
	... 			address = 0x68,
	... 			name    = "Sensor 1",
	... 		),
	... 	},
	... )
	...

	"""

	def __init__(self):
		self.root_node = None

	def load_python(self, file_name):
		with open(file_name, "r") as f:
			local_vars = {
				"mult": Multiplexer,
				"sens": Sensor,
			}
			exec f.read() in globals(), local_vars
			self.root_node = local_vars["root"]


def main():
	cfg = Config()

	for file_name in sys.argv[1:]:
		cfg.load_python(file_name)

	pp = PrettyPrinter()
	pp.format(cfg.root_node)
	pp.writeln()
	#print repr(cfg.root_node)


if __name__ == "__main__":
    main()
