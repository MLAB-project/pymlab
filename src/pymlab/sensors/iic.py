#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors.iic module.

Author: Jan Milik <milikjan@fit.cvut.cz>
"""


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
        self.smbus.write_byte(address, value)
    
    def read_byte(self, address):
        self.smbus.read_byte(address, value)
    
    def write_byte_data(self, address, register, value):
        self.smbus.write_byte_data(address, register, value)
    
    def read_byte_data(self, address, register):
        self.smbus.read_byte_data(address, register)
    
    def write_block_data(self, address, register, value):
        self.smbus.write_block_data(address, register, value)
    
    def read_block_data(self, address, register):
        self.smbus.read_block_data(address, register)


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


def load_driver(port):
    try:
        import smbus
        driver = SMBusDriver(smbus.SMBus(port))
    except ImportError:
        # NOTE: neznam presne jmeno toho HID modulu, ktery chcete pouzivate
        import hid
        # Sem doplnit inicializaci driver. Neco jako:
        # driver = HIDDriver(hid.Bus(port))
        raise NotImplementedError()
    return driver


def init(port):
    DRIVER = load_driver(port)


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

