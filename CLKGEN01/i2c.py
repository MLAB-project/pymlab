#!/usr/bin/python

import sys
import rr
import time


class COpenCoresI2C:

    # OpenCores I2C registers description
    R_PREL = 0x0
    R_PREH = 0x4
    R_CTR = 0x8
    R_TXR = 0xC
    R_RXR = 0xC
    R_CR = 0x10
    R_SR = 0x10

    CTR_EN = (1<<7)

    CR_STA = (1<<7)
    CR_STO = (1<<6)
    CR_RD = (1<<5)
    CR_WR = (1<<4)
    CR_ACK = (1<<3)

    SR_RXACK = (1<<7)
    SR_TIP = (1<<1)


    def wr_reg(self, addr, val):
        self.bus.iwrite(0, self.base_addr +  addr, 4, val)

    def rd_reg(self,addr):
        return self.bus.iread(0, self.base_addr + addr, 4)

    # Function called during object creation
    #   bus = host bus (PCIe, VME, etc...)
    #   base_addr = I2C core base address
    #   prescaler = SCK prescaler, prescaler = (Fsys/(5*Fsck))-1
    def __init__(self, bus, base_addr, prescaler):
        self.bus = bus
        self.base_addr = base_addr
        self.wr_reg(self.R_CTR, 0)
        #print("prescaler: %.4X") % prescaler
        self.wr_reg(self.R_PREL, (prescaler & 0xff))
        #print("PREL: %.2X") % self.rd_reg(self.R_PREL)
        self.wr_reg(self.R_PREH, (prescaler >> 8))
        #print("PREH: %.2X") % self.rd_reg(self.R_PREH)
        self.wr_reg(self.R_CTR, self.CTR_EN)
        #print("CTR: %.2X") % self.rd_reg(self.R_CTR)
        if(not(self.rd_reg(self.R_CTR) & self.CTR_EN)):
            print "Warning! I2C core is not enabled!"

    def wait_busy(self):
        while(self.rd_reg(self.R_SR) & self.SR_TIP):
            pass

    def start(self, addr, write_mode):
        addr = addr << 1
        if(write_mode == False):
            addr = addr | 1
        self.wr_reg(self.R_TXR, addr)
        #print("R_TXR: %.2X") % self.rd_reg(self.R_TXR)
       	self.wr_reg(self.R_CR, self.CR_STA | self.CR_WR)
       	self.wait_busy()

       	if(self.rd_reg(self.R_SR) & self.SR_RXACK):
            raise Exception('No ACK upon address (device 0x%x not connected?)' % addr)
            return "nack"
        else:
            return "ack"

    def write(self, data, last):
        self.wr_reg(self.R_TXR, data)
        cmd = self.CR_WR
        if(last):
            cmd = cmd | self.CR_STO
        self.wr_reg(self.R_CR, cmd)
        self.wait_busy()
        if(self.rd_reg(self.R_SR) & self.SR_RXACK):
            raise Exception('No ACK upon write')

    def read(self, last):
        cmd = self.CR_RD
        if(last):
            cmd = cmd | self.CR_STO | self.CR_ACK
        self.wr_reg(self.R_CR, cmd)
        self.wait_busy()

        return self.rd_reg(self.R_RXR)

    def scan(self):
        periph_addr = []
        for i in range(0,128):
            addr = i << 1
            addr |= 1
            self.wr_reg(self.R_TXR, addr)
            self.wr_reg(self.R_CR, self.CR_STA | self.CR_WR)
            self.wait_busy()

            if(not(self.rd_reg(self.R_SR) & self.SR_RXACK)):
                periph_addr.append(i)
                print("Device found at address: 0x%.2X") % i
                self.wr_reg(self.R_TXR, 0)
                self.wr_reg(self.R_CR, self.CR_STO | self.CR_WR)
                self.wait_busy()

        return periph_addr


##########################################
# Usage example
#gennum = rr.Gennum();
#i2c = COpenCoresI2C(gennum, 0x80000, 500);
