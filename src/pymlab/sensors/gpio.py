#!/usr/bin/python

import time
import sys
import logging

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class I2CIO_TCA9535(Device):
    'Python library for SC18IS602B chip in I2CSPI MLAB bridge module.'

    def __init__(self, parent = None, address = 0x27, **kwargs):
        Device.__init__(self, parent, address, **kwargs)
        
        'The Input Port registers (registers 0 and 1) reflect the incoming logic levels of the pins, regardless of whether thepin is defined as an input or an output by the Configuration Register. It only acts on read operation. Writes to these registers have no effect. The default value, X, is determined by the externally applied logic level. Before a read operation, a write transmission is sent with the command byte to let the I 2 C device know that the Input Port registers will be accessed next.'
        self.INPUT_PORT0 = 0x00
        self.INPUT_PORT1 = 0x01

        'The Output Port registers (registers 2 and 3) show the outgoing logic levels of the pins defined as outputs by the Configuration register. Bit values in this register have no effect on pins defined as inputs. In turn, reads from this register reflect the value that is in the flip-flop controlling the output selection, not the actual pin value.'
        self.OUTPUT_PORT0 = 0x02
        self.OUTPUT_PORT1 = 0x03

        'The Polarity Inversion registers (registers 4 and 5) allow polarity inversion of pins defined as inputs by the Configuration register. If a bit in this register is set (written with 1), the corresponding pins polarity is inverted. If a bit in this register is cleared (written with a 0), the corresponding pins original polarity is retained.'
        self.CONFIG_INVERSION_PORT0 = 0x04
        self.CONFIG_INVERSION_PORT1 = 0x05

        'The Configuration registers (registers 6 and 7) configure the directions of the I/O pins. If a bit in this register is set to 1, the corresponding port pin is enabled as an input with a high-impedance output driver. If a bit in this register is cleared to 0, the corresponding port pin is enabled as an output.'
        self.CONFIG_DIRECTION_PORT0 = 0x06
        self.CONFIG_DIRECTION_PORT1 = 0x07

    def config_ports(self, direction, inversion):
        'Sets INPUT (1) or OUTPUT (0) direction on pins. Inversion setting is applicable for input pins  1-inverted 0-noninverted input polarity.' 
        self.bus.write_wdata(self.address, self.CONFIG_DIRECTION_PORT0, direction);
        self.bus.write_wdata(self.address, self.CONFIG_INVERSION_PORT0, inversion);
        return


    def set_ports(self, value):
        'Writes specified value to the pins defined as output by config_ports() method. Writing to input pins has no effect.' 
        self.bus.write_int16(self.address, self.OUTPUT_PORT0, value);
        return

    def get_ports(self):
        'Reads logical values at pins.' 
        return self.bus.read_wdata(self.address, self.INPUT_PORT0);
        


def main():
    print __doc__


if __name__ == "__main__":
    main()
