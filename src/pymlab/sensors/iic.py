#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors.iic module.

Author: Jan Milik <milikjan@fit.cvut.cz>
"""


import logging


LOGGER = logging.getLogger(__name__)


class Driver(object):
    def write_byte(self, address, value):
        raise NotImplementedError()
    
    def read_byte(self, address):
        raise NotImplementedError()
    
    def write_byte_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_byte_data(address, register):
        raise NotImplementedError()
    
    def write_block_data(address, register, value):
        raise NotImplementedError()
    
    def read_block_data(address, register):
        raise NotImplementedError()


class SMBusDriver(Driver):
    def __init__(self, port, smbus):
        self.port = port
        self.smbus = smbus
    
    def write_byte(self, address, value):
        return self.smbus.write_byte(address, value)
    
    def read_byte(self, address):
        return self.smbus.read_byte(address, value)
    
    def write_byte_data(self, address, register, value):
        return self.smbus.write_byte_data(address, register, value)
    
    def read_byte_data(self, address, register):
        return self.smbus.read_byte_data(address, register)
    
    def write_block_data(self, address, register, value):
        return self.smbus.write_block_data(address, register, value)
    
    def read_block_data(self, address, register):
        return self.smbus.read_block_data(address, register)


class HIDDriver(Driver):
    def write_byte(self, address, value):
        raise NotImplementedError()
    
    def read_byte(self, address):
        raise NotImplementedError()
    
    def write_byte_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_byte_data(self, address, register):
        raise NotImplementedError()
    
    def write_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_block_data(self, address, register):
        raise NotImplementedError()


DRIVER = None


def load_driver(**kwargs):
    port = kwargs.get("port", None)
    if port is not None:
        try:
            import smbus
            LOGGER.info("Loading SMBus driver...")
            return SMBusDriver(port, smbus.SMBus(port))
        except ImportError:
            LOGGER.warning("Failed to import 'smbus' module. SMBus driver cannot be loaded.")
    else:
        LOGGER.warning("SMBus port not specified, skipping trying to load smbus driver.")
    
    try:
        import hid
        LOGGER.info("Loading HID driver...")
        raise NotImplementedError("HID driver is not implemented yet.")
    except ImportError:
        LOGGER.warning("Failed to import 'hid' module. HID driver cannot be loaded.")
    
    raise RuntimeError("Failed to load I2C driver.")
    

def init(**kwargs):
    DRIVER = load_driver(**kwargs)


def write_byte(address, value):
    return DRIVER.write_byte(address, value)
    

def read_byte(address):
    return DRIVER.read_byte(address)


def write_byte_data(address, register, value):
    return DRIVER.write_byte_data(address, register, value)


def read_byte_data(address, register):
    return DRIVER.read_byte_data(address, register)


def write_block_data(address, register, value):
    return DRIVER.write_block_data(address, register, value)


def read_block_data(address, register):
    return DRIVER.read_block_data(address, register)


def main():
    print __doc__


if __name__ == "__main__":
    main()

