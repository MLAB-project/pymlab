#!/usr/bin/python

# Python driver for MLAB frequency counter design wrapper class

import math
import time
import sys

from pymlab.sensors import Device


class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class ACOUNTER02(Device):
    """
    Example:

    .. code-block:: python
    
        #!/usr/bin/python

        # Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

        import smbus
        import struct
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

    def __init__(self, parent = None, address = 0x51, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def read_count(self):
        b0 = self.bus.read_byte(0x00)
        b1 = self.bus.read_byte(0x01)
        b2 = self.bus.read_byte(0x02)
        b3 = self.bus.read_byte(0x03)
        sys.stdout.write("\r\nCount: " + hex(b0) + hex(b1) + hex(b2) + hex(b3))
        return (b3 << 24 + b2 << 16 + b1 << 8 + b0)

    def get_freq(self):
        count = self.read_count()
        return (count/9999900.0)  * 1e7


if __name__ == "__main__":
    while True:
        sys.stdout.write("\r\nFrequency: " + self.get_freq() + "     ")
        sys.stdout.flush()
        time.sleep(15)

