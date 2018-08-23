#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import logging
import struct
import warnings

#from pymlab import config
from pymlab.utils import obj_repr
from pymlab.sensors import iic


LOGGER = logging.getLogger(__name__)


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
    """Base class for all MLAB sensors.

    .. attribute:: channel

       I2C hub channel number to which the device is connected. Channels
       are numbered from 0 (on a 8 channel hub, the channels
       have numbers 0-7). This attribute has no meaning if the device
       isn't connected to a I2C hub
       (see :class:`pymlab.sensors.i2chub02.I2CHub`).

    """

    def __init__(self, parent = None, address = 0x70, **kwargs):
        self.parent  = parent
        self.address = address
        self.possible_addresses = kwargs.get("possible_addresses", [])
        self.channel = kwargs.get("channel", None)
        self.name    = kwargs.get("name", None)

        self.routing_disabled = False

    def __repr__(self):
        if self.name is not None:
            return obj_repr(self, address = self.address, name = self.name)
        return obj_repr(self, address = self.address)

    @property
    def bus(self):
        if self.parent is None:
            return None
        if isinstance(self.parent, Bus):
            return self.parent
        return self.parent.bus

    def get_named_devices(self):
        if self.name is None:
            return {}
        return { self.name: self, }

    def route(self, child = None):
        if self.routing_disabled:
            return False

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

    def initialize(self):
        """This method does nothing, it is meant to be overriden
        in derived classes. Also, this method is not meant to be called
        directly by the user, normally a call to
        :meth:`pymlab.sensors.Bus.initialize` should be used.

        Perform any initialization of the device that
        may require communication. This is meant to be done
        after the configuration has been set up (after instantiating
        :class:`pymlab.config.Config` and setting it up)."""
        pass

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
        return iter(self.children.values())

    def __getitem__(self, key):
        return self.children[key]

    def get_named_devices(self):
        result = {}
        for child in self:
            result.update(child.get_named_devices())
        return result

    def route(self, child = None):
        if self.routing_disabled:
            return False

        if child is None:
            return Device.route(self)

        if child.address not in self.children:
            return False
        return True

    def add_child(self, device):
        if device.address in self.children:
            raise Exception("")
        self.children[device.address] = device
        device.parent = self

    def initialize(self):
        """See :meth:`pymlab.sensors.Device.initialize` for more information.

        Calls `initialize()` on all devices connected to the bus.
        """
        Device.initialize(self)
        for child in iter(self.children.values()):
            child.initialize()


class Bus(SimpleBus):
    INT8  = struct.Struct(">b")
    INT16 = struct.Struct(">h")
    UINT16 = struct.Struct(">H")
    port = None


    def __init__(self, **kwargs):
        SimpleBus.__init__(self, None)

        self._driver = kwargs.pop("driver", None)
        self._driver_config = dict(kwargs)

        self._named_devices = None

    def __repr__(self):
        return obj_repr(self, port = self.port)

    @property
    def driver(self):
        if self._driver is None:
            self._driver = iic.load_driver(**self._driver_config)
        return self._driver

    def get_device(self, name):
        if self._named_devices is None:
            self._named_devices = self.get_named_devices()
        return self._named_devices[name]

    def write_byte(self, address, value):
        """Writes the byte to unaddressed register in a device. """
        LOGGER.debug("Writing byte %s to device %s!", bin(value), hex(address))
        return self.driver.write_byte(address, value)

    def read_byte(self, address):
        """Reads unadressed byte from a device. """
        LOGGER.debug("Reading byte from device %s!", hex(address))
        return self.driver.read_byte(address)

    def write_byte_data(self, address, register, value):
        """Write a byte value to a device's register. """
        LOGGER.debug("Writing byte data %s to register %s on device %s",
            bin(value), hex(register), hex(address))
        return self.driver.write_byte_data(address, register, value)

    def read_byte_data(self, address, register):
        data = self.driver.read_byte_data(address, register)
        LOGGER.debug("Reading byte %s from register %s in device %s", hex(data),  hex(register), hex(address))
        return data

    def write_word_data(self, address, register, value):
        """Write a 16-bit value to a device's register. """
        LOGGER.debug("Writing byte data %s to register %s on device %s",
            bin(value), hex(register), hex(address))
        return self.driver.write_word_data(address, register, value)

    def read_word_data(self, address, register):
        data = self.driver.read_word_data(address, register)
        LOGGER.debug("Reading word %s from register %s in device %s", hex(data),  hex(register), hex(address))
        return data

    def write_block_data(self, address, register, value):
        return self.driver.write_block_data(address, register, value)

    def read_block_data(self, address, register):
        LOGGER.debug("Reading SMBus data block %s from register %s in device %s",value, hex(register), hex(address))
        return self.driver.read_block_data(address, register)

    def write_i2c_block_data(self, address, register, value):
        LOGGER.debug("Writing I2C data block %s from register %s in device %s",value, hex(register), hex(address))
        return self.driver.write_i2c_block_data(address, register, value)

    def read_i2c_block_data(self, address, register, length = 1):
        data = self.driver.read_i2c_block_data(address, register, length)
        LOGGER.debug("Reading I2C data block %s from register %s in device %s", data, hex(register), hex(address))
        return data

    def write_i2c_block(self, address, value):
        LOGGER.debug("Writing I2C data block %s to device %s",value, hex(address))
        return self.driver.write_i2c_block(address, value)

    def read_i2c_block(self, address, length):
        data = self.driver.read_i2c_block(address, length)
        LOGGER.debug("Reading I2C data block %s from device %s", data, hex(address))
        return data

    def write_int16(self, address, register, value):
        value = struct.unpack("<H", struct.pack(">H", value))[0]
        return self.driver.write_word_data(address, register, value)

    def read_int16(self, address):   ## Reads int16 as two separate bytes, suppose autoincrement of internal register pointer in I2C device.
        MSB = self.driver.read_byte(address)
        LSB = self.driver.read_byte(address)
        data = bytes(bytearray([MSB, LSB]))
        LOGGER.debug("MSB %s and LSB %s from device %s was read",  hex(MSB), hex(LSB), hex(address))
        return self.INT16.unpack(data)[0]

    def read_int16_data(self, address, register):            ## Must be checked, possible bug in byte manipulation (LTS01A sensor sometimes returns wrong values)
        data = struct.pack("<H",self.driver.read_word_data(address, register))
        LOGGER.debug("MSB and LSB %r was read from device %s", data, hex(address))
        return self.INT16.unpack(data)[0]


    def read_uint16(self, address):         ## Reads uint16 as two separate bytes, suppose autoincrement of internal register pointer in I2C device.
        MSB = self.driver.read_byte(address)
        LSB = self.driver.read_byte(address)
        data = bytes(bytearray([MSB, LSB]))
        LOGGER.debug("Read MSB %s and LSB %s from device %s",  hex(MSB), hex(LSB), hex(address))
        return self.UINT16.unpack(data)[0]

    def read_uint16_data(self, address, register):            ## Must be checked, possible bug in byte manipulation (LTS01A sensor sometimes returns wrong values)
        data = struct.pack("<H",self.driver.read_word_data(address, register))
        return self.UINT16.unpack(data)[0]

    def get_driver(self):
        return self.driver.get_driver()


    def write_wdata(self, address, register, value):
        """Write a word (two bytes) value to a device's register. """
        warnings.warn("write_wdata() is deprecated and will be removed in future versions replace with write_word_data()", DeprecationWarning)
        LOGGER.debug("Writing word data %s to register %s on device %s",
            bin(value), hex(register), hex(address))
        return self.driver.write_word_data(address, register, value)

    def read_wdata(self, address, register):
        warnings.warn("read_wdata() is deprecated and will be removed in future versions replace with read_word_data()", DeprecationWarning)
        data = self.driver.read_word_data(address, register)
        return data

def main():
    print(__doc__)


if __name__ == "__main__":
    main()
