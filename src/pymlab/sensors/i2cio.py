#!/usr/bin/python
import time

from pymlab.sensors import Device

#TODO: Set only one pin, not all bus

class I2CIO(Device):
    'Python library for I2CIO01A MLAB module with Texas Instruments TCA9535 I/O expander'

    def __init__(self, parent = None, address = 0x27, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.IO_INPUT0 = 0x00
        self.IO_INPUT1 = 0x01
        self.IO_OUTPUT0 = 0x02
        self.IO_OUTPUT1 = 0x03
        self.IO_POLARITY0 = 0x04
        self.IO_POLARITY1 = 0x05
        self.IO_CONFIGURATION0 = 0x06
        self.IO_CONFIGURATION1 = 0x07


    def get_port0(self):
        self.bus.read_byte_data(self.address, self.IO_INPUT0)


    def get_port1(self):
        self.bus.read_byte_data(self.address, self.IO_INPUT1)


    def set_output0(self, port0):
        self.bus.write_byte_data(self.address, self.IO_OUTPUT0, port0)


    def set_output1(self, port1):
        self.bus.write_byte_data(self.address, self.IO_OUTPUT1, port1)


    def set_polarity0(self, port0):
        self.bus.write_byte_data(self.address, self.IO_POLARITY0, port0)


    def set_polarity1(self, port1):
        self.bus.write_byte_data(self.address, self.IO_POLARITY1, port1)


    def set_config0(self, port0):
        self.bus.write_byte_data(self.address, self.IO_CONFIGURATION0, port0)


    def set_config1(self, port1):
        self.bus.write_byte_data(self.address, self.IO_CONFIGURATION1, port1)


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
