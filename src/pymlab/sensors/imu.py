#!/usr/bin/python

# Python driver for MLAB IMU01A module with MMA8451Q Freescale accelerometer and A3G4250D gyroscope sensors wrapper class
# This code is adopted from: 

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


class IMU01_ACC(Device):
    """
    MMA8451Q Accelerometer sensor binding
    
    """

    def __init__(self, parent = None, address = 0x1C, sensitivity = 4.0, highres = True,  **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.MMA_845XQ_STATUS    = 0x00
        self.MMA_845XQ_OUT_X_MSB    = 0x1
        self.MMA_845XQ_OUT_Y_MSB    = 0x3
        self.MMA_845XQ_OUT_Z_MSB    = 0x5

        self.MMA_845XQ_CTRL_REG1    = 0x2A
        self.MMA_845XQ_CTRL_REG1_VALUE_ACTIVE = 0x01
        self.MMA_845XQ_CTRL_REG1_VALUE_F_READ = 0x02

        self.MMA_845XQ_CTRL_REG2 = 0x2B
        self.MMA_845XQ_CTRL_REG2_RESET = 0x40
        self.MMA_845XQ_CTRL_REG3 = 0x2C
        self.MMA_845XQ_CTRL_REG4 = 0x2D
        self.MMA_845XQ_CTRL_REG5 = 0x2E
        self.MMA_845XQ_WHO_AM_I = 0x0D

        self.MMA_845XQ_PL_STATUS = 0x10
        self.MMA_845XQ_PL_CFG = 0x11
        self.MMA_845XQ_PL_EN = 0x40

        self.MMA_845XQ_XYZ_DATA_CFG = 0x0E
        self.MMA_845XQ_2G_MODE = 0x00 # Set Sensitivity to 2g
        self.MMA_845XQ_4G_MODE = 0x01 # Set Sensitivity to 4g
        self.MMA_845XQ_8G_MODE = 0x02 # Set Sensitivity to 8g

        self.MMA_845XQ_FF_MT_CFG = 0x15
        self.MMA_845XQ_FF_MT_CFG_ELE = 0x80
        self.MMA_845XQ_FF_MT_CFG_OAE = 0x40

        self.MMA_845XQ_FF_MT_SRC = 0x16
        self.MMA_845XQ_FF_MT_SRC_EA = 0x80

        self.MMA_845XQ_PULSE_CFG = 0x21
        self.MMA_845XQ_PULSE_CFG_ELE = 0x80

        self.MMA_845XQ_PULSE_SRC = 0x22
        self.MMA_845XQ_PULSE_SRC_EA = 0x80

        ## Interrupts

        # Auto SLEEP/WAKE interrupt
        self.INT_ASLP = (1<<7)
        # Transient interrupt
        self.INT_TRANS = (1<<5)
        # Orientation = (landscape/portrait) interrupt
        self.INT_LNDPRT = (1<<4)
        # Pulse detection interrupt
        self.INT_PULSE = (1<<3)
        # Freefall/Motion interrupt
        self.INT_FF_MT = (1<<2)
        # Data ready interrupt
        self.INT_DRDY = (1<<0)

        SCALES = {
            2.0: self.MMA_845XQ_2G_MODE,
            4.0: self.MMA_845XQ_4G_MODE,
            8.0: self.MMA_845XQ_8G_MODE,
        }

        self._sensitivity = sensitivity
        self._highres = highres
        self._scale = SCALES[sensitivity]

    def standby(self):
        reg1 = self.bus.read_byte_data(self.address, self.MMA_845XQ_CTRL_REG1)   # Set to status reg
        self.bus.write_byte_data(self.address, self.MMA_845XQ_CTRL_REG1, (reg1 & ~self.MMA_845XQ_CTRL_REG1_VALUE_ACTIVE))

    def active(self):
        reg1 = self.bus.read_byte_data(self.address, self.MMA_845XQ_CTRL_REG1)   # Set to status reg
        self.bus.write_byte_data(self.address, self.MMA_845XQ_CTRL_REG1, (reg1 | self.MMA_845XQ_CTRL_REG1_VALUE_ACTIVE | (0 if (self._highres == True) else self.MMA_845XQ_CTRL_REG1_VALUE_F_READ) ))

    def initialize(self):
        if self._scale == self.MMA_845XQ_2G_MODE:
            self.step_factor = (0.0039 if (self._highres == True) else 0.0156) # Base value at 2g setting
        elif self._scale == self.MMA_845XQ_4G_MODE:
            self.step_factor = 2*(0.0039 if (self._highres == True) else 0.0156)
        elif self._scale == self.MMA_845XQ_8G_MODE:
            self.step_factor = 4*(0.0039 if (self._highres == True) else 0.0156)
        else:
            LOGGER.error("Uknown sensitivity value",)

        whoami = self.bus.read_byte_data(self.address, self.MMA_845XQ_WHO_AM_I); # Get Who Am I from the device.
        # return value for MMA8543Q is 0x3A
          
        self.bus.write_byte_data(self.address, self.MMA_845XQ_CTRL_REG2, self.MMA_845XQ_CTRL_REG2_RESET)       # Reset
        time.sleep(0.5) # Give it time to do the reset
        self.standby()
        self.bus.write_byte_data(self.address, self.MMA_845XQ_PL_CFG, (0x80 | self.MMA_845XQ_PL_EN))       # Set Portrait/Landscape mode
        self.bus.write_byte_data(self.address, self.MMA_845XQ_XYZ_DATA_CFG, self._scale)     #setup sensitivity
        self.active()

    def getPLStatus(self):
        return self.bus.read_byte_data(self.address, self.MMA_845XQ_PL_STATUS)

    def getPulse(self):
        self.bus.write_byte_data(self.address, self.MMA_845XQ_PULSE_CFG, self.MMA_845XQ_PULSE_CFG_ELE)
        return (self.bus.read_byte_data(self.address, self.MMA_845XQ_PULSE_SRC) & self.MMA_845XQ_PULSE_SRC_EA)


    def axes(self):
        self._stat = self.bus.read_byte_data(self.address, self.MMA_845XQ_STATUS)       # read status register, data registers follows. 
        if(self._highres):
            x = self.bus.read_int16_data(self.address, self.MMA_845XQ_OUT_X_MSB) / 64.0 * self.step_factor
            y = self.bus.read_int16_data(self.address, self.MMA_845XQ_OUT_Y_MSB) / 64.0 * self.step_factor
            z = self.bus.read_int16_data(self.address, self.MMA_845XQ_OUT_Z_MSB) / 64.0 * self.step_factor

        else:
            x = self.bus.read_byte(self.address) * self.step_factor
            y = self.bus.read_byte(self.address) * self.step_factor
            z = self.bus.read_byte(self.address) * self.step_factor

        return (x,y,z)

    def setInterrupt(self, interrupt_type, pin, on):
        current_value = self.bus.read_byte_data(self.address, self.MMA_845XQ_CTRL_REG4)

        if (on == True):
            current_value |= interrupt_type
        else:
            current_value &= ~(interrupt_type)

        self.bus.write_byte_data(self.address, self.MMA_845XQ_CTRL_REG4, current_value);

        current_routing_value = self.bus.read_byte_data(self.address, self.MMA_845XQ_CTRL_REG5);

        if (pin == 1):
            current_routing_value &= ~(type);

        elif (pin == 2):
            current_routing_value |= type;
        else:
            LOGGER.error("Uknown interrupt pin",)

        self.bus.write_byte_data(self.address, self.MMA_845XQ_CTRL_REG5, current_routing_value)

    def disableAllInterrupts(self):
        self.bus.write_byte_data(self.address, self.MMA_845XQ_CTRL_REG4, 0)


class IMU01_GYRO(Device):
    """
    A3G4250D Gyroscope sensor binding. Needs sensitivity calibration data. This gyroscope is factory calibrated to sensitivity range from 7.4 to 10.1 mdps/digit. The 8.75 mdps/digit is selected as default value. 
    
    """

    def __init__(self, parent = None, address = 0x68, sensitivity_corr = (8.75, 8.75, 8.75), datarate = 0b00, bandwidth = 0b00, FIFO = True, HPF = True,   **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.sensitivity = (sensitivity_corr[0]/1000 , sensitivity_corr[1]/1000, sensitivity_corr[2]/1000)
        self.data_rate = datarate
        self.band_width = bandwidth
        self.FIFO_EN = FIFO
        self.HPen = HPF
    
        self.A3G4250D_WHO_AM_I   = 0x0F
        self.A3G4250D_CTRL_REG1    = 0x20
        self.A3G4250D_CTRL_REG2    = 0x21
        self.A3G4250D_CTRL_REG3    = 0x22
        self.A3G4250D_CTRL_REG4    = 0x23
        self.A3G4250D_CTRL_REG5    = 0x24
        self.A3G4250D_REFERENCE   = 0x25
        self.A3G4250D_OUT_TEMP   = 0x26
        self.A3G4250D_STATUS_REG   = 0x27
        self.A3G4250D_OUT_X_L   = 0x28
        self.A3G4250D_OUT_X_H   = 0x29
        self.A3G4250D_OUT_Y_L   = 0x2A
        self.A3G4250D_OUT_Y_H   = 0x2B
        self.A3G4250D_OUT_Z_L   = 0x2C
        self.A3G4250D_OUT_Z_H   = 0x2D
        self.A3G4250D_FIFO_CTRL_REG    = 0x2e
        self.A3G4250D_FIFO_SRC_REG    = 0x2F
        self.A3G4250D_INT1_CFG    = 0x30
        self.A3G4250D_INT1_SRC    = 0x31
        self.A3G4250D_INT1_TSH_XH    = 0x32
        self.A3G4250D_INT1_TSH_XL    = 0x33
        self.A3G4250D_INT1_TSH_YH    = 0x34
        self.A3G4250D_INT1_TSH_YL    = 0x35
        self.A3G4250D_INT1_TSH_ZH    = 0x36
        self.A3G4250D_INT1_TSH_ZL    = 0x37
        self.A3G4250D_INT1_DURATION    = 0x38
        
        self.A3G4250D_FIFO_BYPASS_MODE  = 0b000
        self.A3G4250D_FIFO_MODE  = 0b001
        self.A3G4250D_FIFO_STREAM_MODE  = 0b010


    def initialize(self):
        self.bus.write_byte_data(self.address, self.A3G4250D_CTRL_REG1, ((self.data_rate << 6) | (self.band_width << 4) | 0x0f))  ## setup data rate and bandwidth. All axis are active
        self.bus.write_byte_data(self.address, self.A3G4250D_CTRL_REG5, ((self.FIFO_EN << 7) | (self.HPen << 4) | 0x0f))  ## setup data rate and bandwidth. All axis are active
 
        self.bus.write_byte_data(self.address, self.A3G4250D_FIFO_CTRL_REG, (self.A3G4250D_FIFO_BYPASS_MODE  << 5))     
        if (self.bus.read_byte_data(self.address, self.A3G4250D_WHO_AM_I) != 0b11010011):
            raise NameError('Gyroscope device could not be identified')

    def axes(self):
        INT16 = struct.Struct("<h")

        self.bus.write_byte_data(self.address, self.A3G4250D_CTRL_REG1, ((self.data_rate << 6) | (self.band_width << 4) | 0b1000))  ## setup data rate and 
        self.bus.read_byte_data(self.address, self.A3G4250D_OUT_X_L)
#        x = self.bus.read_int16(self.address)
#        y = self.bus.read_int16(self.address)
#        z = self.bus.read_int16(self.address)

#        YLSB = self.bus.read_byte(self.address)
#        YMSB = self.bus.read_byte(self.address)

#        ZLSB = self.bus.read_byte(self.address)
#        ZMSB = self.bus.read_byte(self.address)

#        XLSB = self.bus.read_byte(self.address)
#        XMSB = self.bus.read_byte(self.address)

#        y = self.bus.read_wdata(self.address, self.A3G4250D_OUT_Y_L)
#        z = self.bus.read_wdata(self.address, self.A3G4250D_OUT_Z_L)
#        x = self.bus.read_wdata(self.address, self.A3G4250D_OUT_X_L)

#        print hex(YLSB),hex(YMSB),hex(ZLSB),hex(ZMSB),hex(XLSB),hex(XMSB)

#        return (x*self.sensitivity[0], y*self.sensitivity[1], z*self.sensitivity[2])

        LSB = self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_X_L)
        MSB = self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_X_H)
        x = (MSB << 8) + LSB
        if (x & 0x1000):
            x -= 65536

        LSB = self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_Y_L)
        MSB = self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_Y_H)
        y = (MSB << 8) + LSB
        if (y & 0x1000):
            y -= 65536

        LSB = self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_Z_L)
        MSB = self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_Z_H)
        z = (MSB << 8) + LSB
        if (z & 0x1000):
            z -= 65536

#        print hex(YLSB),hex(YMSB),hex(ZLSB),hex(ZMSB),hex(XLSB),hex(XMSB)


#        return (hex(self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_X_L)), hex(self.bus.read_byte_data(self.address,  self.A3G4250D_OUT_X_H)))

#        self.bus.write_byte_data(self.address, self.A3G4250D_CTRL_REG5, ((self.FIFO_EN << 7) | (self.HPen << 4) | 0x0f))  ## setup data rate and 
        self.bus.write_byte_data(self.address, self.A3G4250D_CTRL_REG1, ((self.data_rate << 6) | (self.band_width << 4) | 0b1111))  ## setup data rate and 
        self.bus.write_byte_data(self.address, self.A3G4250D_FIFO_CTRL_REG, (self.A3G4250D_FIFO_BYPASS_MODE  << 5))     

        return (x, y, z)


    def temp(self):
        temp = self.bus.read_byte_data(self.address, self.A3G4250D_OUT_TEMP)
        return temp

