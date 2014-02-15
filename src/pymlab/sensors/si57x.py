#!/usr/bin/python

import math
import time
import sys

from pymlab.sensors import Device


class CLKGEN01(Device):

    def __init__(self, parent = None, address = 0x55, gauss = 1.3, declination = (0,0), **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.R_HS = 0x07
        self.R_RFREQ4 = 0x08
        self.R_RFREQ3 = 0x09
        self.R_RFREQ2 = 0x0A
        self.R_RFREQ1 = 0x0B
        self.R_RFREQ0 = 0x0C
        self.R_RFMC = 0x87
        self.R_FDCO = 0x89

        self.HS_DIV_MASK = 0xE0
        self.N1_H_MASK = 0x1F
        self.N1_L_MASK = 0xC0
        self.RFREQ4_MASK = 0x3F

        self.RFMC_RST = (1<<7)
        self.RFMC_NEW_FREQ = (1<<6)
        self.RFMC_FREEZE_M = (1<<5)
        self.RFMC_FREEZE_VCADC = (1<<4)
        self.RFMC_RECALL = (1<<0)

        self.FDCO_FREEZE_DCO = (1<<4)

    def get_rfreq(self):
        rfreq = self.bus.read_byte_data(self.address,self.R_RFREQ0)
        rfreq += (self.bus.read_byte_data(self.address,self.R_RFREQ1)<<8)
        rfreq += (self.bus.read_byte_data(self.address,self.R_RFREQ2)<<16)
        rfreq += (self.bus.read_byte_data(self.address,self.R_RFREQ3)<<24)
        rfreq += ((self.bus.read_byte_data(self.address,self.R_RFREQ4) & self.RFREQ4_MASK)<<32)
        return (rfreq>>28)+((rfreq & 0x0FFFFFFF)/2.0**28)

    def get_n1_div(self):
        n1 = ((self.bus.read_byte_data(self.address, self.R_RFREQ4) & self.N1_L_MASK)>>6)
        n1 += ((self.bus.read_byte_data(self.address, self.R_HS) & self.N1_H_MASK)<<2)
        return n1

    def get_hs_div(self):
        return ((self.bus.read_byte_data(self.address, self.R_HS))>>5)

    def set_rfreq(self, freq):
        self.bus.write_byte_data(self.address, self.R_RFERQ0, (freq & 0xFF))
        self.bus.write_byte_data(self.address, self.R_RFERQ1, ((freq>>8) & 0xFF))
        self.bus.write_byte_data(self.address, self.R_RFERQ2, ((freq>>16) & 0xFF))
        self.bus.write_byte_data(self.address, self.R_RFERQ3, ((freq>>24) & 0xFF))
        reg = self.bus.read_byte_data(self.address, self.R_RFERQ4)
        self.bus.write_byte_data(self.address, self.R_RFERQ4, (((freq>>32) & self.RFREQ4_MASK) | (reg & self.N1_L_MASK)))

    def set_hs_div(self, div):
        reg = self.bus.read_byte_data(self.address, self.R_HS)
        self.bus.write_byte_data(self.address, self.R_HS, ((div<<5) | (reg & self.N1_H_MASK)))

    def set_n1_div(self, div):
        reg = self.bus.read_byte_data(self.address, self.R_HS)
        self.bus.write_byte_data(self.address, self.R_HS, ((div>>2) | (reg & self.HS_DIV_MASK)))
        reg = self.bus.read_byte_data(self.address, self.R_RFREQ4)
        self.bus.write_byte_data(self.address, self.R_RFREQ4, (((div & self.N1_L_MASK)<<6) | (reg & self.RFREQ4_MASK)))

    def freeze_m(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_FREEZE_M
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def unfreeze_m(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) & ~(self.RFMC_FREEZE_M)
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def freeze_dco(self):
        self.bus.write_byte_data(self.address, self.R_RDCO, self.FDCO_FREEZE_DCO)

    def unfreeze_dco(self):
        self.bus.write_byte_data(self.address, self.R_RDCO, 0)

    def reset_reg(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_RST
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def recall_nvm(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_RECALL
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    # For Si571 only !
    def freeze_vcadc(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_FREEZE_VCADC
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def unfreeze_vcadc(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) & ~(self.RFMC_FREEZE_VCADC)
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)
