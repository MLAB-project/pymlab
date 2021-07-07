#!/usr/bin/python

#import smbus
import time
import sys

from pymlab.sensors import Device


class AS3935(Device):
    'Python library for LIGHTNING01A MLAB module with austria microsystems AS3935 I2C/SPI lighting detecor.'
    def __init__(self, parent = None, address = 0x02,  TUN_CAP = 0, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        addresses = [0x02, 0x01, 0x03]

        if address not in addresses:
            raise ValueError("Unsupported sensor address")

        self._TUN_CAP = TUN_CAP

    def soft_reset(self):
        self.bus.write_byte_data(self.address, 0x3c, 0x96);
        return

    def reset(self):
        self.soft_reset()
        self.setTUN_CAP(self._TUN_CAP)

    def calib_rco(self):
        """calibrate RCO"""
        byte = self.bus.read_byte_data(self.address, 0x08)
        self.bus.write_byte_data(self.address, 0x3d, 0x96);
        print(bin(self.bus.read_byte_data(self.address, 0x3A)))
        print(bin(self.bus.read_byte_data(self.address, 0x3B)))
        return

    def antennatune_on(self, FDIV = 0,TUN_CAP=0):
        """Display antenna resonance at IRQ pin"""
        # set frequency division
        data = self.bus.read_byte_data(self.address, 0x03)
        data = (data & (~(3<<6))) | (FDIV<<6)
        self.bus.write_byte_data(self.address, 0x03, data)
        #print hex(self.bus.read_byte_data(self.address, 0x03))

        self.setTUN_CAP(TUN_CAP)

        # Display LCO on IRQ pin
        reg = self.bus.read_byte_data(self.address, 0x08)
        reg = (reg & 0x8f) | 0x80;
        self.bus.write_byte_data(self.address, 0x08, reg)
        return

    def initialize(self):
        self.soft_reset()
        self.setTUN_CAP(self._TUN_CAP)

    def getDistance(self):
        data = self.bus.read_byte_data(self.address, 0x07) & 0b00111111
        print(hex(data))

        distance = {0b111111: 255,
            0b101000: 40,
            0b100101: 37,
            0b100010: 34,
            0b011111: 31,
            0b011011: 27,
            0b011000: 24,
            0b010100: 20,
            0b010001: 17,
            0b001110: 14,
            0b001100: 12,
            0b001010: 10,
            0b001000: 8,
            0b000110: 6,
            0b000101: 5,
            0b000001: 0}

        return distance.get(data,data)  # returns distance or distance data adirectly in case there is no distance code.

    def getIndoor(self):
        indoor = self.bus.read_byte_data(self.address, 0x00) &  0b00111110
        values = {
            0b100100: True,
            0b011100: False}
        try:
          return values[indoor]
        except LookupError:
          print("Uknown register value {0:b}".format(indoor))

    def setIndoor(self, state):
        byte = self.bus.read_byte_data(self.address, 0x00)
        if state:
            byte |= 0b100100
            byte &=~0b011010
        else:
            byte |= 0b011100
            byte &=~0b100010
        #print("{:08b}".format(byte))
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

    def setTUN_CAP(self, value):
        # Display LCO on IRQ pin
        reg = self.bus.read_byte_data(self.address, 0x08)
        reg = (reg & 0x0f) | value;
        self.bus.write_byte_data(self.address, 0x08, reg)

    def getTUN_CAP(self):
        data = self.bus.read_byte_data(self.address, 0x08)
        data = data & 0x0f
        return data

    def setWDTH(self, value):
        data = self.bus.read_byte_data(self.address, 0x01)
        data = (data & (~(0x0f))) | (value)
        self.bus.write_byte_data(self.address, 0x01, data)

    def getWDTH(self):
        data = self.bus.read_byte_data(self.address, 0x01)
        return (data & 0x0f)

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
        return not bool(self.bus.read_byte_data(self.address, 0x00) & 0b1) #returns true in Active state

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
