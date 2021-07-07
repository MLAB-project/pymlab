#!/usr/bin/python

import math
import time
import sys

from pymlab.sensors import Device


class CLKGEN01(Device):

    """Lilbary for Si571 and Si570 clock generator ICs"""

    def __init__(self, parent = None, address = 0x55, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.R_HS = 7
        self.R_RFREQ4 = 8
        self.R_RFREQ3 = 9
        self.R_RFREQ2 = 10
        self.R_RFREQ1 = 11
        self.R_RFREQ0 = 12
        self.R_RFMC = 135
        self.R_FDCO = 137

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
        rfreq |= (self.bus.read_byte_data(self.address,self.R_RFREQ1)<<8)
        rfreq |= (self.bus.read_byte_data(self.address,self.R_RFREQ2)<<16)
        rfreq |= (self.bus.read_byte_data(self.address,self.R_RFREQ3)<<24)
        rfreq |= ((self.bus.read_byte_data(self.address,self.R_RFREQ4) & self.RFREQ4_MASK)<<32)
        return rfreq/2.0**28

    def get_n1_div(self):
        n1 = ((self.bus.read_byte_data(self.address, self.R_HS) & self.N1_H_MASK)<<2)
        n1 |= self.bus.read_byte_data(self.address, self.R_RFREQ4)>>6
        return n1+1

    def get_hs_div(self):
        return (((self.bus.read_byte_data(self.address, self.R_HS))>>5) + 4)

    def set_rfreq(self, freq):
        freq_int = int(freq * (2.0**28))
        reg = self.bus.read_byte_data(self.address, self.R_RFREQ4)
        self.bus.write_byte_data(self.address, self.R_RFREQ4, (((freq_int>>32) & self.RFREQ4_MASK) | (reg & self.N1_L_MASK)))
        self.bus.write_byte_data(self.address, self.R_RFREQ0, (freq_int & 0xFF))
        self.bus.write_byte_data(self.address, self.R_RFREQ1, ((freq_int>>8) & 0xFF))
        self.bus.write_byte_data(self.address, self.R_RFREQ2, ((freq_int>>16) & 0xFF))
        self.bus.write_byte_data(self.address, self.R_RFREQ3, ((freq_int>>24) & 0xFF))

    def set_hs_div(self, div):
        reg = self.bus.read_byte_data(self.address, self.R_HS)
        self.bus.write_byte_data(self.address, self.R_HS, (((div-4)<<5) | (reg & self.N1_H_MASK)))

    def set_n1_div(self, div):
        div = div - 1
        reg = self.bus.read_byte_data(self.address, self.R_HS)
        self.bus.write_byte_data(self.address, self.R_HS, (((div>>2) & self.N1_H_MASK) | (reg & self.HS_DIV_MASK)))
        reg = self.bus.read_byte_data(self.address, self.R_RFREQ4)
        self.bus.write_byte_data(self.address, self.R_RFREQ4, (((div<<6) & self.N1_L_MASK) | (reg & self.RFREQ4_MASK)))

    def freeze_m(self):
        self.bus.write_byte_data(self.address, self.R_RFMC, self.RFMC_FREEZE_M)

    def unfreeze_m(self):
        self.bus.write_byte_data(self.address, self.R_RFMC, 0)

    def new_freq(self):
        self.bus.write_byte_data(self.address, self.R_RFMC, self.RFMC_NEW_FREQ)

    def reset(self):			#Will interrupt I2C state machine. It is not reccomended for starting from initial conditions.
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_RST
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def freeze_dco(self):
        self.bus.write_byte_data(self.address, self.R_FDCO, self.FDCO_FREEZE_DCO)

    def unfreeze_dco(self):
        self.bus.write_byte_data(self.address, self.R_FDCO, 0)

    def reset_reg(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_RST
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def recall_nvm(self): # reloads NVM data. It is recommended for starting from initial conditions.
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_RECALL
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def set_freq(self, fout, freq):
        """
        Sets new output frequency, required parameters are real current frequency at output and new required frequency.
        """
        hsdiv_tuple = (4, 5, 6, 7, 9, 11)           # possible dividers
        n1div_tuple = (1,) + tuple(range(2,129,2))  #
        fdco_min = 5670.0           # set maximum as minimum
        hsdiv = self.get_hs_div()   # read curent dividers
        n1div = self.get_n1_div()   #

        if abs((freq-fout)*1e6/fout) > 3500:  # check if new requested frequency is withing 3500 ppm from last Center Frequency Configuration
            # Large change of frequency
            fdco = fout * hsdiv * n1div # calculate high frequency oscillator
            fxtal =  fdco / self.get_rfreq()  # should be fxtal = 114.285

            for hsdiv_iter in hsdiv_tuple:      # find dividers with minimal power consumption
                for n1div_iter in n1div_tuple:
                    fdco_new = freq * hsdiv_iter * n1div_iter
                    if (fdco_new >= 4850) and (fdco_new <= 5670):
                        if (fdco_new <= fdco_min):
                            fdco_min = fdco_new
                            hsdiv = hsdiv_iter
                            n1div = n1div_iter
            rfreq = fdco_min / fxtal

            self.freeze_dco()       # write registers
            self.set_hs_div(hsdiv)
            self.set_n1_div(n1div)
            self.set_rfreq(rfreq)
            self.unfreeze_dco()
            self.new_freq()
        else:
            # Small change of frequency
            rfreq = self.get_rfreq() * (freq/fout)

            self.freeze_m()         # write registers
            self.set_rfreq(rfreq)
            self.unfreeze_m()


    # For Si571 only !
    def freeze_vcadc(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) | self.RFMC_FREEZE_VCADC
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)

    def unfreeze_vcadc(self):
        reg = self.bus.read_byte_data(self.address, self.R_RFMC) & ~(self.RFMC_FREEZE_VCADC)
        self.bus.write_byte_data(self.address, self.R_RFMC, reg)
