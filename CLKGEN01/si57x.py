#!/usr/bin/python

import sys
import rr
import time
import i2c


class CSi57x:

    R_HS = 0x07
    R_RFREQ4 = 0x08
    R_RFREQ3 = 0x09
    R_RFREQ2 = 0x0A
    R_RFREQ1 = 0x0B
    R_RFREQ0 = 0x0C
    R_RFMC = 0x87
    R_FDCO = 0x89

    HS_DIV_MASK = 0xE0
    N1_H_MASK = 0x1F
    N1_L_MASK = 0xC0
    RFREQ4_MASK = 0x3F

    RFMC_RST = (1<<7)
    RFMC_NEW_FREQ = (1<<6)
    RFMC_FREEZE_M = (1<<5)
    RFMC_FREEZE_VCADC = (1<<4)
    RFMC_RECALL = (1<<0)

    FDCO_FREEZE_DCO = (1<<4)


    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr

    def rd_reg(self, addr):
        self.i2c.start(self.addr, True)
        self.i2c.write(addr, False)
        self.i2c.start(self.addr, False)
        reg = self.i2c.read(True)
        #print("raw data from Si570: %.2X")%reg
        return reg

    def wr_reg(self, addr, data):
        self.i2c.start(self.addr, True)
        self.i2c.write(addr, False)
        self.i2c.write(data, True)

    def get_rfreq(self):
        rfreq = self.rd_reg(self.R_RFREQ0)
        rfreq += (self.rd_reg(self.R_RFREQ1)<<8)
        rfreq += (self.rd_reg(self.R_RFREQ2)<<16)
        rfreq += (self.rd_reg(self.R_RFREQ3)<<24)
        rfreq += ((self.rd_reg(self.R_RFREQ4) & self.RFREQ4_MASK)<<32)
        return (rfreq>>28)+((rfreq & 0x0FFFFFFF)/2.0**28)

    def get_n1_div(self):
        n1 = ((self.rd_reg(self.R_RFREQ4) & self.N1_L_MASK)>>6)
        n1 += ((self.rd_reg(self.R_HS) & self.N1_H_MASK)<<2)
        return n1

    def get_hs_div(self):
        return ((self.rd_reg(self.R_HS))>>5)

    def set_rfreq(self, freq):
        self.wr_reg(self.R_RFERQ0, (freq & 0xFF))
        self.wr_reg(self.R_RFERQ1, ((freq>>8) & 0xFF))
        self.wr_reg(self.R_RFERQ2, ((freq>>16) & 0xFF))
        self.wr_reg(self.R_RFERQ3, ((freq>>24) & 0xFF))
        reg = self.rd_reg(self.R_RFERQ4)
        self.wr_reg(self.R_RFERQ4, (((freq>>32) & self.RFREQ4_MASK) | (reg & self.N1_L_MASK)))

    def set_hs_div(self, div):
        reg = self.rd_reg(self.R_HS)
        self.wr_reg(self.R_HS, ((div<<5) | (reg & self.N1_H_MASK)))

    def set_n1_div(self, div):
        reg = self.rd_reg(self.R_HS)
        self.wr_reg(self.R_HS, ((div>>2) | (reg & self.HS_DIV_MASK)))
        reg = self.rd_reg(self.R_RFREQ4)
        self.wr_reg(self.R_RFREQ4, (((div & self.N1_L_MASK)<<6) | (reg & self.RFREQ4_MASK)))

    def freeze_m(self):
        reg = self.rd_reg(self.R_RFMC) | self.RFMC_FREEZE_M
        self.wr_reg(self.R_RFMC, reg)

    def unfreeze_m(self):
        reg = self.rd_reg(self.R_RFMC) & ~(self.RFMC_FREEZE_M)
        self.wr_reg(self.R_RFMC, reg)

    def freeze_dco(self):
        self.wr_reg(self.R_RDCO, self.FDCO_FREEZE_DCO)

    def unfreeze_dco(self):
        self.wr_reg(self.R_RDCO, 0)

    def reset_reg(self):
        reg = self.rd_reg(self.R_RFMC) | self.RFMC_RST
        self.wr_reg(self.R_RFMC, reg)

    def recall_nvm(self):
        reg = self.rd_reg(self.R_RFMC) | self.RFMC_RECALL
        self.wr_reg(self.R_RFMC, reg)

    # For Si571 only !
    def freeze_vcadc(self):
        reg = self.rd_reg(self.R_RFMC) | self.RFMC_FREEZE_VCADC
        self.wr_reg(self.R_RFMC, reg)

    def unfreeze_vcadc(self):
        reg = self.rd_reg(self.R_RFMC) & ~(self.RFMC_FREEZE_VCADC)
        self.wr_reg(self.R_RFMC, reg)
