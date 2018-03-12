#!/usr/bin/python

#import smbus
import time

from pymlab.sensors import Device


#TODO: Implement output data checksum checking

class ATMEGA(Device):
    'Python library for ATmega MLAB module.'

    def __init__(self, parent = None, address = 0x04, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def put(self,data):
        self.bus.write_byte(self.address, data);

    def get(self):
        data = self.bus.read_byte(self.address);
        return data


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
