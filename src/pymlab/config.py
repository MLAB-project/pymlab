#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.config module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import sys
import json

from utils import obj_repr, PrettyPrinter
from pymlab.sensors import Bus, SimpleBus


class Node(object):
    def __init__(self, config, address, name = None):
        self.config  = config
        self.parent  = None
        self.channel = None
        self.address = address
        self.name    = name

        config.add_node(self)

    def __repr__(self):
        return obj_repr(self, self.address, self.name)

    def __pprint__(self, printer, level = 0):
        printer.write("%s  %d  %s" % (type(self).__name__, self.address, self.name, ))


class Config(object):
    """
    Example:

    >>> cfg = Config()
    >>> cfg.load_python("config_file.py")

    Contents of `config_file.py`:

    .. code-block:: python

        root = mult(
            address = 0x70,
            name    = "Multiplexer 1",
            children = {
                0x01: mult(
                    address = 0x72,
                    name    = "Multiplexer 2",
                    children = {
                        0x01: sens(
                            address = 0x68,
                            name    = "Sensor 2",
                        ),
                    },
                ),
                0x03: sens(
                    address = 0x68,
                    name    = "Sensor 1",
                ),
            },
        )
    
    """

    def __init__(self, **kwargs):
        self.drivers = {}
        
        self.i2c_config = {}
        self._bus = None
        
        self.init_drivers()

        self.config(**kwargs)
    
    @property
    def bus(self):
        if self._bus is None:
            self._bus = Bus(**self.i2c_config)
        return self._bus
    
    def init_drivers(self):
        from pymlab.sensors import lts, mag, sht25, i2chub, altimet, acount, clkgen
        self.drivers = {
            "i2chub": i2chub.I2CHub,

            "lts01": lts.LTS01,
            "mag01": mag.MAG01,
            "sht25": sht25.SHT25,
            "altimet01": altimet.ALTIMET01,
            "acount02": acount.ACOUNTER02,
            "clkgen01": clkgen.CLKGEN01,
        }

    def get_device(self, name):
        return self.bus.get_device(name)
    
    def build_device(self, value, parent = None):
        if isinstance(value, list) or isinstance(value, tuple):
            if parent is None:
                result = Bus(**self.i2c_config)
            else:
                result = SimpleBus(parent)
            for child in value:
                result.add_child(self.build_device(child, result))
            return result

        if isinstance(value, dict):
            if "type" not in value:
                raise ValueError("Device dictionary doesn't have a \"type\" item.")

            try:
                fn = self.drivers[value["type"]]
            except KeyError:
                raise ValueError("Unknown device type: {!r}".format(value["type"]))

            kwargs = dict(value)
            kwargs.pop("type")

            children = kwargs.pop("children", [])

            result = fn(**kwargs)

            for child in children:
                result.add_child(self.build_device(child, result))

            return result

        if isinstance(value, Device):
            return value

        raise ValueError("Cannot create a device from: {!r}!".format(value))
    
    def config(self, **kwargs):
        self.i2c_config = kwargs.get("i2c", {})
        self._bus = self.build_device(kwargs.get("bus", []))
    
    def load_python(self, source):
        local_vars = {
            "cfg":  self,
            #"mult": self._mult,
            #"sens": self._sens,
            #"mult": Multiplexer,
            #"sens": Sensor,
        }
        exec source in globals(), local_vars
        #self.port = local_vars.get("port", self.port)
        self.i2c_config = local_vars.get("i2c", {})
        self._bus = self.build_device(local_vars.get("bus", []))
    
    def load_file(self, file_name):
        if file_name.endswith(".py"):
            with open(file_name, "r") as f:
                return self.load_python(f.read())
        raise ValueError("Unknown file type: {!r}".format(file_name))

    def initialize(self):
        self.bus.initialize()


def main():
    cfg = Config()

    for file_name in sys.argv[1:]:
        cfg.load_python(file_name)

    pp = PrettyPrinter()
    pp.format(cfg.root_node)
    pp.writeln()

    for name, node in cfg.named_nodes.iteritems():
        print "%s: %r" % (name, node, )
    #print repr(cfg.root_node)


if __name__ == "__main__":
    main()
