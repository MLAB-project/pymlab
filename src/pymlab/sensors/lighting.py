#!/usr/bin/python

#import smbus
import time
import sys

from pymlab.sensors import Device


class AS3935(Device):
    'Python library for LIGHTNING01A MLAB module with austria microsystems AS3935 I2C/SPI lighting detecor.'
    def __init__(self, parent = None, address = 0x02, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def soft_reset(self):
        self.bus.write_byte_data(self.address, 0x3c, 0x96);
        return

    def reset(self):
        self.soft_reset()

    def calib_rco(self):
        self.bus.write_byte_data(self.address, 0x3d, 0x96);
        return

    def initialize(self):
        pass

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


    def getNoiseFloor(self):
        value = (self.bus.read_byte_data(self.address, 0x01) & 0b01110000) >> 4
        indoor = self.getIndoor()
        matrix = [
            [390, 28],
            [630, 45],
            [860, 62],
            [1100,78],
            [1140,95],
            [1570,112],
            [1800,130],
            [2000,146]]
        return matrix[value][int(indoor)]

    def setNoiseFloor(self, value):
        data = self.bus.read_byte_data(self.address, 0x01)
        data = (data & (~(7<<4))) | (value<<4)
        self.bus.write_byte_data(self.address, 0x01, data)

    def setNoiseFloorAdv(self, value):
        pass


    def getSpikeRejection(self):
        data = self.bus.read_byte_data(self.address, 0x02) & 0b1111
        return data

    def setSpikeRejection(self, value):
        data = self.bus.read_byte_data(self.address, 0x02) & 0b1111
        data = (data & (~(0b1111))) | (value)
        self.bus.write_byte_data(self.address, 0x02, data)

    def getPowerStatus(self):
        return not bool(self.bus.read_byte_data(self.address, 0x00) & 0b1)

    def getInterrupts(self):
        reg = self.bus.read_byte_data(self.address, 0x03)
        out = {}
        out['INT_NH'] = bool(reg & 0b00000001)
        out['INT_D']  = bool(reg & 0b00000100)
        out['INT_L']  = bool(reg & 0b00001000)
        return out

    def getSingleEnergy(self):
        lsb = self.bus.read_byte_data(self.address, 0x04)
        msb = self.bus.read_byte_data(self.address, 0x05)
        mmsb= self.bus.read_byte_data(self.address, 0x06) & 0b11111
        return lsb | msb << 8 | mmsb << 16

    def getMaskDist(self):
        return bool(self.bus.read_byte_data(self.address, 0x03) & 0b00100000)

    def setMaskDist(self, value):
        value = bool(value)
        data = self.bus.read_byte_data(self.address, 0x03)
        if value:
            self.bus.write_byte_data(self.address, 0x03, data | 0b00100000)
        else:
            self.bus.write_byte_data(self.address, 0x03, data & (~0b00100000))


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
