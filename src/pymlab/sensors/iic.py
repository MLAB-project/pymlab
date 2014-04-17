#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors.iic module.

Author: Jan Milik <milikjan@fit.cvut.cz>
"""
import time

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
    
    def write_word_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_word_data(self, address, register):
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
        return self.smbus.read_byte(address)
    
    def write_byte_data(self, address, register, value):
        return self.smbus.write_byte_data(address, register, value)
    
    def read_byte_data(self, address, register):
        return self.smbus.read_byte_data(address, register)

    def write_word_data(self, address, register, value):
        return self.smbus.write_word_data(address, register, value)
    
    def read_word_data(self, address, register):
        return self.smbus.read_word_data(address, register)
    
    def write_block_data(self, address, register, value):
        return self.smbus.write_block_data(address, register, value)
    
    def read_block_data(self, address, register):
        return self.smbus.read_block_data(address, register)


class HIDDriver(Driver):
    def __init__(self):
        time.sleep(1)   # give an OS time for remounting the HID device
        import hid
        self.h = hid.device(0x10C4, 0xEA90) # Connect HID again after enumeration
        self.h.write([0x02, 0xFF, 0x00, 0x00, 0x00])  # Set GPIO to Open-Drain  
        for k in range(3):      # blinking LED
            self.h.write([0x04, 0x00, 0xFF])
            time.sleep(0.1)
            self.h.write([0x04, 0xFF, 0xFF])
            time.sleep(0.1)
        self.h.write([0x02, 0xFF, 0x00, 0xFF, 0x00])  # Set GPIO to RX/TX LED  
        # Set SMB Configuration (AN 495)
        self.h.write([0x06, 0x00, 0x01, 0x86, 0xA0, 0x02, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x01, 0x00, 0x0F])  
    
    def write_byte(self, address, value):
        return self.h.write([0x14, address<<1, 0x01, value]) # Data Write Request
    
    def read_byte(self, address):
        self.h.write([0x10, address<<1, 0x00, 0x01]) # Data Read Request
        for k in range(10):
            self.h.write([0x15, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                self.h.write([0x12, 0x00, 0x01]) # Data Read Force
                response = self.h.read(4)
                return response[3]
        LOGGER.warning("CP2112 Byte Read Error...")
        return 0xFF
    
    def write_byte_data(self, address, register, value):
        return self.h.write([0x14, address<<1, 0x02, register, value]) # Data Write Request
    
    def read_byte_data(self, address, register):
        self.h.write([0x11, address<<1, 0x00, 0x01, 0x01, register]) # Data Write Read Request
        for k in range(10):
            self.h.write([0x15, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                self.h.write([0x12, 0x00, 0x01]) # Data Read Force
                response = self.h.read(4)
                return response[3]
        LOGGER.warning("CP2112 Read Error...")
        return 0xFF
    
    def write_word_data(self, address, register, value):
        # TODO: Implement HIDDrive.write_word_data()
        raise NotImplementedError()
    
    def read_word_data(self, address, register):
        # TODO: Implement HIDDrive.read_word_data()
        raise NotImplementedError()
    
    def write_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_block_data(self, address, register):
        raise NotImplementedError()


DRIVER = None


def load_driver(**kwargs):
    try:
        LOGGER.info("Loading HID driver...")
        import hid
        LOGGER.info("Initiating HID driver...")
        try:
            h = hid.device(0x10C4, 0xEA90) # Try Connect HID
            h.write([0x01, 0x01]) # Reset Device for cancelling all transfers and reset configuration
            h.close()
            return HIDDriver() # We can use this connection
        except IOError:
            LOGGER.info("HID device does not exist, we will try SMBus directly...")
    
    except ImportError:
        LOGGER.info("HID driver does not exist, we will try SMBus driver...")
 
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
    
    raise RuntimeError("Failed to load I2C driver. Enable logging for more details.")


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

