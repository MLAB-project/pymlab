#!/usr/bin/python

# Python driver for MLAB LION1CELL01B module

import math
import time
import sys
import logging
import time

from pymlab.sensors import Device

import struct

LOGGER = logging.getLogger(__name__)

class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class LIONCELL(Device):
    """
    Battery Guage binding
    
    """

    def __init__(self, parent = None, address = 0x55, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    # reset
    def reset(self):           
        self.bus.write_byte_data(self.address, 0x00, 0x01)
        self.bus.write_byte_data(self.address, 0x00, 0x41)

    # deg C
    def getTemp(self):           
        return (self.bus.read_byte_data(self.address, 0x0C) + self.bus.read_byte_data(self.address, 0x0D) * 256) * 0.1 - 273.15

    # mAh
    def getRemainingCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x04) + self.bus.read_byte_data(self.address, 0x05) * 256)

    # mAh
    def FullChargeCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x06) + self.bus.read_byte_data(self.address, 0x07) * 256)

    # mAh
    def NominalAvailableCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x14) + self.bus.read_byte_data(self.address, 0x15) * 256)
 
    # mAh
    def FullAvailabeCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x16) + self.bus.read_byte_data(self.address, 0x17) * 256)

    # 10 mWhr
    def AvailableEnergy(self):
        return (self.bus.read_byte_data(self.address, 0x24) + self.bus.read_byte_data(self.address, 0x25) * 256)

    # mAh
    def DesignCapacity(self):
        return (self.bus.read_byte_data(self.address, 0x3c) + self.bus.read_byte_data(self.address, 0x3d) * 256)

    # V
    def Voltage(self):
        return (self.bus.read_byte_data(self.address, 0x08) + self.bus.read_byte_data(self.address, 0x09) * 256)

    # %
    def StateOfCharge(self):
        """ % of Full Charge """
        return (self.bus.read_byte_data(self.address, 0x02) + self.bus.read_byte_data(self.address, 0x03) * 256)


    # mA
    def AverageCurrent(self):
        I = (self.bus.read_byte_data(self.address, 0x0A) + self.bus.read_byte_data(self.address, 0x0B) * 256)
        if (I & 0x8000):
            return -0x10000 + I
        else:
            return I

    # S.N.
    def SerialNumber(self):
        return (self.bus.read_byte_data(self.address, 0x7E) + self.bus.read_byte_data(self.address, 0x7F) * 256)

    # Pack Configuration
    def PackConfiguration(self):
        return (self.bus.read_byte_data(self.address, 0x3A) + self.bus.read_byte_data(self.address, 0x3B) * 256)

    def Chemistry(self):
        ''' Get cells chemistry '''
        length = self.bus.read_byte_data(self.address, 0x79) 
        chem = []
        for n in range(length):
            chem.append(self.bus.read_byte_data(self.address, 0x7A + n)) 
        return chem
            

    # Read Flash Block
    # return 32 bytes plus checksum
    def ReadFlashBlock(self, fclass, fblock):
        ret = []
        self.bus.write_byte_data(self.address, 0x61, 0x00)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x3E, fclass)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x3F, fblock)
        time.sleep(0.1)
        fsum = 0
        for addr in range(0,32):
            tmp = self.bus.read_byte_data(self.address, 0x40+addr)
            ret.append(tmp)
            fsum = (fsum + tmp) % 256
        ret.append(self.bus.read_byte_data(self.address, 0x60))        
        return ret

    # Write Byte to Flash
    def WriteFlashByte(self, fclass, fblock, foffset, fbyte):
        self.bus.write_byte_data(self.address, 0x61, 0x00)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x3E, fclass)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x3F, fblock)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x40+foffset, fbyte)
        time.sleep(0.1)
        fsum = 0
        for addr in range(0,32):
            if(addr != foffset):
                tmp = self.bus.read_byte_data(self.address, 0x40+addr)
                fsum = (fsum + tmp) % 256
        fsum = (fsum + fbyte) % 256
        fsum = 0xFF-fsum
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, 0x60, fsum)        
        time.sleep(1)
        

