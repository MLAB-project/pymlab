#!/usr/bin/python

#import smbus
import time
import sys

from pymlab.sensors import Device


class AS3935(Device):
    'Python library for LIGHTNING01A MLAB module with austria microsystems AS3935 I2C/SPI lighting detecor.'
    def __init__(self, parent = None, address = 0x03, **kwargs):
        Device.__init__(self, parent, address, **kwargs)


    def soft_reset(self):
        #self.bus.write_byte(self.address, self.SOFT_RESET);
        return

    def setup(self, setup_reg ):  # writes to status register and returns its value
        pass

    def initialize(self):
        print("INITIALIZATION ..........")

        print(self.bus.read_i2c_block(self.address,0x07))

        #for reg in list(range(0x00,0x09))+[0x3a, 0x3b]:
        #    data = self.bus.read_byte_data(self.address, reg)
        #    print("register", hex(reg), "data", "0x{:02x}   0b{:08b}".format(data, data))
        #    time.sleep(0.1)

    def getDistance(self):
        distance = self.bus.read_byte_data(self.address, 0x07) & 0b00111111
        if distance < 2:
            distance = 0 # storm is over head
        elif distance > 62:
            distance = 99 # storm is out of range
        return distance

    def getAFEgain(self):
        gain = self.bus.read_byte_data(self.address, 0x00) & 0b00111110
        return gain

    def getIndoor(self):
        indoor = self.bus.read_byte_data(self.address, 0x00) &  0b00111110
        if indoor == 0b100100:
            return True
        elif indoor == 0b011100:
            return False
        else:
            pass #TODO chybova hlaska, ve toto neni znamo
    def getOutdoor(self):
        return not self.getIndoor()

    def getNoiseFloor(self):
        value = self.bus.read_byte_data(self.address, 0x01) & 0b01110000 >> 3
        outdoor = self.getIndoor()
        matrix = [
            [390, 28],
            [630, 45],
            [860, 62],
            [1100,78],
            [1140,95],
            [1570,112],
            [1800,130],
            [2000,146]]
        return matrix[value][int(outdoor)]



    def setIndoor(self, state):
        byte = self.bus.read_byte_data(self.address, 0x00)
        if state:
            byte |= 0b100100
            byte &=~0b011010
        else:
            byte |= 0b011100
            byte &=~0b100010
        print("{:08b}".format(byte))
        self.bus.write_byte_data(self.address, 0x00, byte)
        return byte

    def getPowerStatus(self):
        return bool(self.bus.read_byte_data(self.address, 0x00) & 0b1)

    def getInterrupts(self):
        reg = self.bus.read_byte_data(self.address, 0x03)
        out = {}
        out['INT_NH'] = reg & 0b00000001
        out['INT_D']  = reg & 0b00000100
        out['INT_N']  = reg & 0b00001000
        return out



def main():
    print(__doc__)


if __name__ == "__main__":
    main()
