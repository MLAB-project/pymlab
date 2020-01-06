#!/usr/bin/python

# Python driver for MLAB IMU01A module with MMA8451Q Freescale accelerometer and A3G4250D gyroscope sensors wrapper class
# This code is adopted from: 

import math
import time
import sys
import logging

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

    # https://www.invensense.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
class MPU6050(Device):
    
    MPU6050_ACCEL_XOUT_H = 0x3B
    MPU6050_ACCEL_XOUT_L = 0x3C
    MPU6050_ACCEL_YOUT_H = 0x3D
    MPU6050_ACCEL_YOUT_L = 0x3E
    MPU6050_ACCEL_ZOUT_H = 0x3F
    MPU6050_ACCEL_ZOUT_L = 0x40
    MPU6050_TEMP_OUT_H = 0x41
    MPU6050_TEMP_OUT_L = 0x42
    MPU6050_GYRO_XOUT_H = 0x43
    MPU6050_GYRO_XOUT_L = 0x44
    MPU6050_GYRO_YOUT_H = 0x45
    MPU6050_GYRO_YOUT_L = 0x46
    MPU6050_GYRO_ZOUT_H = 0x47
    MPU6050_GYRO_ZOUT_L = 0x78
        
    def __init__(self, parent = None, address = 0x68, possible_adresses = [0x68, 0x69],  **kwargs):
        Device.__init__(self, parent, address, **kwargs)
    
    def initialize(self):
        self.bus.write_byte_data(self.address, 0x6b, 0x00) # power management 1

    def get_accel(self):
        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_ACCEL_XOUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_ACCEL_XOUT_L)
        x = (MSB << 8) + LSB
        if (x >= 0x8000):
            x = -1*((65535 - x) + 1)

        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_ACCEL_YOUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_ACCEL_YOUT_L)
        y = (MSB << 8) + LSB
        if (y >= 0x8000):
            y = -1*((65535 - y) + 1)

        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_ACCEL_ZOUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_ACCEL_ZOUT_L)
        z = (MSB << 8) + LSB
        if (z >= 0x8000):
            z = -1*((65535 - z) + 1)

        return(x/16384.0,y/16384.0,z/16384.0)


    def get_temp(self):
        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_TEMP_OUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_TEMP_OUT_L)
        t = (MSB << 8) + LSB

        return(t/340+36.5)


    def get_gyro(self):
        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_GYRO_XOUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_GYRO_XOUT_L)
        x = (MSB << 8) + LSB

        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_GYRO_YOUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_GYRO_YOUT_L)
        y = (MSB << 8) + LSB

        MSB = self.bus.read_byte_data(self.address,  self.MPU6050_GYRO_ZOUT_H)
        LSB = self.bus.read_byte_data(self.address,  self.MPU6050_GYRO_ZOUT_L)
        z = (MSB << 8) + LSB

        return(x/131,y/131,z/131)

    def dist(self, a,b):
        return math.sqrt((a*a)+(b*b))

    def get_rotation(self, position = None):
        if position:
            (x, y, z) = position
        else:
            (x, y, z) = self.get_accel()
         
        radians = math.atan2(y, self.dist(x,z))
        rx = math.degrees(radians)

        radians = math.atan2(x, self.dist(y,z))
        ry = -math.degrees(radians)

        return (rx, ry)



class WINDGAUGE03A(Device):

    def __init__(self, parent = None, address = 0x68, **kwargs):
        Device.__init__(self, parent, address, **kwargs)
    
        self.SDP33_i2c_address = 0x21
        self.mag_i2c_address = 0x0C

        ## USER BANK 0 REGISTERS
        self.ICM20948_WHO_AM_I = 0x00
        self.ICM20948_USER_CTRL = 0x03
        self.ICM20948_LP_CONFIG = 0x05
        self.ICM20948_PWR_MGMT_1 = 0x06
        self.ICM20948_PWR_MGMT_2 = 0x07
        self.ICM20948_INT_PIN_CFG = 0x0F
        self.ICM20948_INT_ENABLE = 0x10
        self.ICM20948_I2C_MST_STATUS = 0x17
        self.ICM20948_ACEL_XOUT_H = 0x2D
        self.ICM20948_ACEL_XOUT_L = 0x2E
        self.ICM20948_ACEL_YOUT_H = 0x2F
        self.ICM20948_ACEL_YOUT_L = 0x30
        self.ICM20948_ACEL_ZOUT_H = 0x31
        self.ICM20948_ACEL_XOUT_L = 0x32
        self.ICM20948_GYRO_XOUT_H = 0x33
        self.ICM20948_GYRO_XOUT_L = 0x34
        self.ICM20948_GYRO_YOUT_H = 0x35
        self.ICM20948_GYRO_YOUT_L = 0x36
        self.ICM20948_GYRO_ZOUT_H = 0x37
        self.ICM20948_GYRO_XOUT_L = 0x38
        self.ICM20948_TEMP_OUT_H = 0x39
        self.ICM20948_TEMP_OUT_L = 0x3A
        self.ICM20948_EXT_SLV_SENS_DATA_00 = 0x3B

        # USER BANK 2 REGISTERS
        self.ICM20948_GYRO_CONFIG = 0x01
        self.ICM20948_ACEL_CONFIG = 0x14

        ## USER BANK 3 REGISTERS
        self.ICM20948_I2C_SLV0_ADDR = 0x03
        self.ICM20948_I2C_SLV0_REG = 0x04 # I2C slave 0 register address from where to begin data transfer.
        self.ICM20948_I2C_SLV0_CTRL  = 0x05
        self.ICM20948_I2C_SLV0_DO = 0x06

        self.ICM20948_I2C_SLV1_ADDR = 0x07
        self.ICM20948_I2C_SLV1_REG = 0x08 # I2C slave 1 register address from where to begin data transfer.
        self.ICM20948_I2C_SLV1_CTRL  = 0x09
        self.ICM20948_I2C_SLV1_DO = 0x0A

        ## USER BANK REGISTERS 0-3
        self.ICM20948_REG_BANK_SEL = 0x7F # 0

    def usr_bank_sel(self, usr_bank_reg):
        self.bus.write_byte_data(self.address, self.ICM20948_REG_BANK_SEL, usr_bank_reg << 4)

    def write_icm20948_reg_data(self, reg_address, reg_usr_bank, value):
        self.usr_bank_sel(reg_usr_bank)
        self.bus.write_byte_data(self.address, reg_address, value)

    def read_icm20948_reg_data(self, reg_address, reg_usr_bank, num_of_bytes):
        self.usr_bank_sel(reg_usr_bank)
        if num_of_bytes > 1:
            return(self.bus.read_i2c_block_data(self.address, reg_address, num_of_bytes))
        else:
            return((self.bus.read_byte_data(self.address, reg_address)))

    def reset (self):
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x80) # reset device and register values
        time.sleep(1)

    def initialize (self): 
        # self.bus.write_byte_data(self.address, self.ICM20948_PWR_MGMT_2, 0x3f) # gyro and accel off
        # self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_2, 0, 0x00) # gyro and accel on
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00) # I2C_MST_EN set to 0
        self.write_icm20948_reg_data(self.ICM20948_INT_PIN_CFG, 0, 0x02) # BYPASS ENABLE
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x02) # I2C_MST_RST set to 1 (bit auto clears)
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x01) # clear sleep bit and wake up device
        time.sleep(0.1)


    def i2c_master_init (self):
        # self.write_icm20948_reg_data(self.ICM20948_INT_ENABLE, 0, 0xFF) # enable i2c master interrupt to propagate to interrupt pin1
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x02) # I2C_MST_RST
        # time.sleep(0.1)

        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x20) # When bit 5 set (0x20), the transaction does not write a register value, it will only read data, or write data
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, self.SDP33_i2c_address)

        # self.write_icm20948_reg_data(self.ICM20948_LP_CONFIG, 0, 0x00) #disable master's duty cycled mode
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1


    def i2c_master_write (self, slv_id, slv_addr, data_out, slv_reg ): # 
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20)                                     # USER_CTRL[5] (I2C_MST_EN) = 1
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR + (slv_id * 4), 3, slv_addr | (1 << 7))   # I2C_SLVX_ADDR[6:0] = (slv_addr | I2C_SLV0_RNW) - slave addres | R/W bit MSB (1)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO + (slv_id * 4), 3, data_out)                # I2C_SLVX_DO[7:0](0-15) = data_out 
        if slv_reg is not None:
            self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG + (slv_id * 4), 3, slv_reg)               # I2C_SLVX_REG[7:0] = slv_reg
            self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + (slv_id * 4), 3, 0xA0)              # I2C_SLVX_CTRL[7] (I2C_SLVX_EN) = 1, I2C_SLVX_CTRL[5] (I2C_SLVX_REG_EN) = 1
        else:
            self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + (slv_id * 4), 3, 0x80)              # I2C_SLVX_CTRL[7] (I2C(0-15)_SLVX_EN) = 1, I2C_SLVX_CTRL[5] (I2C_SLVX_REG_EN) = 0
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00)                                     # USER_CTRL[5] (I2C_MST_EN) = 0
        time.sleep(0.1)

    def i2c_master_read (self, slv_id, slv_addr, slv_rd_len, slv_reg ): # 
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20)                                     # USER_CTRL[5] (I2C_MST_EN) = 1
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR + (slv_id * 4), 3, slv_addr | (1 << 7))   # I2C_SLVX_ADDR[6:0] = (slv_addr | I2C_SLV0_RNW) - slave addres | R/W bit MSB (0) 
        if slv_reg is not None:
            self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG + (slv_id * 4), 3, slv_reg)            # I2C_SLVX_REG[7:0] = slv_reg
            self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + (slv_id * 4), 3, 0xA0 | slv_rd_len) # I2C_SLVX_CTRL[7] (I2C_SLVX_EN) = 1, I2C_SLVX_CTRL[5] (I2C_SLVX_REG_EN) = 1, I2C_SLVX_LENG[3:0] = slv_rd_len (number of bytes to be read from slave (0-15))
        else:
            self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + (slv_id * 4), 3, 0x80 | slv_rd_len) # I2C_SLVX_CTRL[7] (I2C_SLVX_EN) = 1, I2C_SLVX_CTRL[5] (I2C_SLVX_REG_EN) = 0, I2C_SLVX_LENG[3:0] = slv_rd_len (number of bytes to be read from slave (0-15))
        time.sleep(0.1)

    def i2c_master_sdp33_init(self):
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1
        # time.sleep(0.01)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_DO, 3, 0x04)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_REG, 3, 0x31) # adress of the slave register master will write to 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_ADDR, 3, 0x0C) # R/W bit MSB - write operation
        # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0xA9)   # I2C_SLV1_EN, I2C_SLV1_REG_DIS, I2C_SLV1_LENG[3:0] 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0x00)   # I2C_SLV0_DIS

        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_ADDR, 3, 0xA1) # SPD3X i2c address =0x21 | R/W bit MSB - read (1)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0xA9)   # I2C_SLV1_EN, I2C_SLV1_REG_EN, I2C_SLV1_LENG[3:0] 
        time.sleep(0.1)

        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_REG, 3, 0x00) # adress of the first slave register master will start reading from 
        # print("reading", end = ' ')
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))
        # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0x8f) 

    def i2c_master_mag_init (self):

        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, 0x01) 
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00) # I2C_MST_EN set to 0, I2C_MST_RST set to 1
        # time.sleep(gi)
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 0, I2C_MST_RST set to 1
        # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x02) # I2C_MST_EN set to 0, I2C_MST_RST set to 1
        # time.sleep(0.1)
        

        ## MAGNETOMETER SOFT RESET
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, 0x01) 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG, 3, 0x32) # adress of the slave register master will write to 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 0x0C) # R/W bit MSB - write operation
        # # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x8a)   # I2C_SLV0_EN, I2C_SLV0_REG_EN, I2C_SLV0_LENG[3:0] = 9
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x00)   # I2C_SLV0_DIS

        # time.sleep(gi)

        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, 0x04)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG, 3, 0x31) # adress of the slave register master will write to 
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 0x0C) # R/W bit MSB - write operation
        # time.sleep(gi)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x8a)   # I2C_SLV0_EN, I2C_SLV0_REG_EN, I2C_SLV0_LENG[3:0] = 9
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x00)   # I2C_SLV0_DIS

        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 0x8C) # R/W bit MSB
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG, 3, 0x00) # adress of the first slave register master will start reading from 
        # print("reading", end = ' ')
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))
        # time.sleep(gi)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x8d)   # I2C_SLV0_EN, I2C_SLV0_REG_EN, I2C_SLV0_LENG[3:0] = 9
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1
        time.sleep(0.1)
        # time.sleep(gi)

    def get_temp(self):
        room_temp_offset = 21.0
        tem_sens = 333.87
        temp_raw_data = self.read_icm20948_reg_data(self.ICM20948_TEMP_OUT_H, 0, 2)
        temp_raw = ((temp_raw_data[0] << 8) + temp_raw_data[1])
        return(((temp_raw - room_temp_offset)/temp_sens) + room_temp_offset)

    def get_accel(self):
        accel_sens = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_ACEL_CONFIG, 2, 1) & 0x6))) * 2048)
        accel_raw = self.read_icm20948_reg_data(self.ICM20948_ACEL_XOUT_H, 0, 6)
        accel_x_raw = ((accel_raw[0] << 8) + accel_raw_[1])
        accel_y_raw = ((accel_raw[2] << 8) + accel_raw_[3])
        accel_z_raw = ((accel_raw[4] << 8) + accel_raw_[5])

        if accel_x_raw > 0x7fff:
            accel_x_raw -= 65536
        if accel_y_raw > 0x7fff:
            accel_y_raw -= 65536
        if accel_z_raw > 0x7fff:
            accel_z_raw -= 65536

        return((accel_x_raw / accel_sens), (accel_y_raw / accel_sens), (accel_z_raw / accel_sens) )

    def get_gyro(self):
        gyro_sens = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_GYRO_CONFIG, 2, 1) & 0x6))) * 16.4)
        gyro_raw = self.read_icm20948_reg_data(self.ICM20948_GYRO_XOUT_H, 0, 6)
        gyro_x_raw = ((gyro_raw[0] << 8) + gyro_raw_[1])
        gyro_y_raw = ((gyro_raw[2] << 8) + gyro_raw_[3])
        gyro_z_raw = ((gyro_raw[4] << 8) + gyro_raw_[5])

        if gyro_x_raw > 0x7fff:
            gyro_x_raw -= 65536
        if gyro_y_raw > 0x7fff:
            gyro_y_raw -= 65536
        if gyro_z_raw > 0x7fff:
            gyro_z_raw -= 65536

        return((gyro_x_raw / gyro_sens), (gyro_y_raw / gyro_sens), (gyro_z_raw / gyro_sens))

    
    def SDP33_write (self, SDP33_i2c_address, command):
        self.bus.write_i2c_block_data(self.SDP33_i2c_address, command)


    def SDP33_read (self, SDP33_i2c_address, command):
        # write = i2c_msg.write(SDP33_i2c_address, command)
        # read = i2c_msg.read(SDP33_i2c_address, 9)
        
                # raw_data = bus2.i2c_rdwr(write, read)
        self.bus2.write_i2c_block_data(self, self.SDP33_i2c_address, 0, [0x36, 0x24])
        raw_data = self.bus2.read_i2c_block_data(self, self.SDP33_i2c_address, 9)        
        return(raw_data)

    def get_mag(self, cal_available):

        if (cal_available):
            cal_file = open("ICM20948_mag_cal.txt", "r")
            cal_consts = cal_file.readline().split(",")

            offset_x = float(cal_consts[0])
            offset_y = float(cal_consts[1])
            offset_z = float(cal_consts[2])

            scale_x = float(cal_consts[3])
            scale_y = float(cal_consts[4])
            scale_z = float(cal_consts[5])

            # print(str(offset_x)+"\n")
            # print(str(offset_y)+"\n")
            # print(str(offset_z)+"\n")

            # print(str(scale_x)+"\n")
            # print(str(scale_y)+"\n")
            # print(str(scale_z)+"\n")
        else:
            offset_x, offset_y, offset_z = 0, 0, 0
            scale_x, scale_y, scale_z = 1, 1, 1



        mag_raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00, 0, 13)

        magX = (mag_raw_data[6] << 8) + mag_raw_data[5]
        magY = (mag_raw_data[8] << 8) + mag_raw_data[7]
        magZ = (mag_raw_data[10] << 8) + mag_raw_data[9]

        if magX > 0x7fff:
            magX -= 65536
        if magY > 0x7fff:
            magY -= 65536
        if magZ > 0x7fff:
            magZ -= 65536
        
        mag_scf = 4912/32752.0

        # print(magX)
        # print(((magX*mag_scf) - offset_x) * scale_x)

        

        return(((magX*mag_scf) - offset_x) * scale_x, ((magY*mag_scf) - offset_y) * scale_y, ((magZ*mag_scf) - offset_z)*scale_z)

    def calib_mag(self, calib_time):
        try:
            decision = False
            print("\nDo you wish to perform new magnetometer calibration? Old calibration data will be lost!")
            
                
            while not decision:
                start_cal =  raw_input("[Y/N]\n")
                if (start_cal == 'N') or (start_cal == 'n'):
                    print("\nCalibration canceled, no new calibration values saved.\n\n")
                    sys.exit(1)
                elif (start_cal == 'Y') or (start_cal == 'y'):
                    decision = True

            self.i2c_master_mag_init()
            delay = 5
            print("\nStarting calibration in %d seconds with duration of %d seconds!\n" % (delay,calib_time))
            time.sleep(1)
            for i in range(delay):
                print(str(delay-i))
                time.sleep(1)
            
            print("Calibration has started!\n")            

            t_end = time.time() + calib_time
            mag_x = []
            mag_y = []
            mag_z = []

            while time.time() < t_end:
                mag_x_i, mag_y_i, mag_z_i = self.get_mag(False)
                mag_x.append(mag_x_i)
                mag_y.append(mag_y_i)
                mag_z.append(mag_z_i)
                print("%f,%f,%f\n" % (mag_x_i, mag_y_i, mag_z_i))
         

            ### HARDIRON COMPAS COMPENSATION
          
            offset_x = (max(mag_x) + min(mag_x)) / 2
            offset_y = (max(mag_y) + min(mag_y)) / 2
            offset_z = (max(mag_z) + min(mag_z)) / 2

            ### SOFTIRON COMPASS COMPENSATION

            avg_delta_x = (max(mag_x) - min(mag_x)) / 2
            avg_delta_y = (max(mag_y) - min(mag_y)) / 2
            avg_delta_z = (max(mag_z) - min(mag_z)) / 2

            avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3

            scale_x = avg_delta / avg_delta_x
            scale_y = avg_delta / avg_delta_y
            scale_z = avg_delta / avg_delta_z

            # sys.stdout.write(str(offset_x)+"\n")
            # sys.stdout.write(str(offset_y)+"\n")
            # sys.stdout.write(str(offset_z)+"\n")

            # sys.stdout.write(str(scale_x)+"\n")
            # sys.stdout.write(str(scale_y)+"\n")
            # sys.stdout.write(str(scale_z)+"\n")

            decision = False
            print("\nFinished. Do you wish to save calibration data?")
            
            while not decision:
                start_cal =  raw_input("[Y/N]\n")
                if (start_cal == 'N') or (start_cal == 'n'):
                    print("\nCalibration canceled, no new calibration values saved.\n\n")
                    sys.exit(1)
                elif (start_cal == 'Y') or (start_cal == 'y'):
                    decision = True

        except KeyboardInterrupt:
                
            print("\nCalibration canceled, no new calibration values saved.\n\n")
            sys.exit(0)

        cal_file = open("ICM20948_mag_cal.txt", "w")
        cal_file.write("%f,%f,%f,%f,%f,%f" % (offset_x, offset_y, offset_z, scale_x, scale_y, scale_z))
        cal_file.close()

        sys.stdout.write("Calibration successful!\n\n")



class ICM20948(Device):

    # def __init__(self):
    def __init__(self, parent = None, address = 0x68, **kwargs):
        Device.__init__(self, parent, address, **kwargs)
    
        self.SDP33_i2c_address = 0x21
        self.mag_i2c_address = 0x0C

        ## USER BANK 0 REGISTERS
        self.ICM20948_WHO_AM_I = 0x00
        self.ICM20948_USER_CTRL = 0x03
        self.ICM20948_LP_CONFIG = 0x05
        self.ICM20948_PWR_MGMT_1 = 0x06
        self.ICM20948_PWR_MGMT_2 = 0x07
        self.ICM20948_INT_PIN_CFG = 0x0F
        self.ICM20948_INT_ENABLE = 0x10
        self.ICM20948_I2C_MST_STATUS = 0x17
        self.ICM20948_ACEL_XOUT_H = 0x2D
        self.ICM20948_ACEL_XOUT_L = 0x2E
        self.ICM20948_ACEL_YOUT_H = 0x2F
        self.ICM20948_ACEL_YOUT_L = 0x30
        self.ICM20948_ACEL_ZOUT_H = 0x31
        self.ICM20948_ACEL_XOUT_L = 0x32
        self.ICM20948_GYRO_XOUT_H = 0x33
        self.ICM20948_GYRO_XOUT_L = 0x34
        self.ICM20948_GYRO_YOUT_H = 0x35
        self.ICM20948_GYRO_YOUT_L = 0x36
        self.ICM20948_GYRO_ZOUT_H = 0x37
        self.ICM20948_GYRO_XOUT_L = 0x38
        self.ICM20948_TEMP_OUT_H = 0x39
        self.ICM20948_TEMP_OUT_L = 0x3A
        self.ICM20948_EXT_SLV_SENS_DATA_00 = 0x3B

        # USER BANK 2 REGISTERS
        self.ICM20948_GYRO_CONFIG = 0x01
        self.ICM20948_ACEL_CONFIG = 0x14

        ## USER BANK 3 REGISTERS
        self.ICM20948_I2C_SLV0_ADDR = 0x03
        self.ICM20948_I2C_SLV0_REG = 0x04 # I2C slave 0 register address from where to begin data transfer.
        self.ICM20948_I2C_SLV0_CTRL  = 0x05
        self.ICM20948_I2C_SLV0_DO = 0x06

        self.ICM20948_I2C_SLV1_ADDR = 0x07
        self.ICM20948_I2C_SLV1_REG = 0x08 # I2C slave 1 register address from where to begin data transfer.
        self.ICM20948_I2C_SLV1_CTRL  = 0x09
        self.ICM20948_I2C_SLV1_DO = 0x0A

        ## USER BANK REGISTERS 0-3
        self.ICM20948_REG_BANK_SEL = 0x7F # 0

    def usr_bank_sel(self, usr_bank_reg):
        self.bus.write_byte_data(self.address, self.ICM20948_REG_BANK_SEL, usr_bank_reg << 4)

    def write_icm20948_reg_data(self, reg_address, reg_usr_bank, value):
        self.usr_bank_sel(reg_usr_bank)
        self.bus.write_byte_data(self.address, reg_address, value)

    def read_icm20948_reg_data(self, reg_address, reg_usr_bank, num_of_bytes):
        self.usr_bank_sel(reg_usr_bank)
        if num_of_bytes > 1:
            return(self.bus.read_i2c_block_data(self.address, reg_address, num_of_bytes))
        else:
            return((self.bus.read_byte_data(self.address, reg_address)))

    def reset (self):
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x80) # reset device and register values
        time.sleep(1)

    def initialize (self): 
        # self.write_icm20948_reg_data( self.ICM20948_REG_BANK_SEL, 0, 0x00) # select user register bank 0
        # self.bus.write_byte_data(self.address, self.ICM20948_PWR_MGMT_2, 0x3f) # gyro and accel off
        # self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_2, 0, 0x00) # gyro and accel on
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1
        # time.sleep(0.1)
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00) # I2C_MST_EN set to 0
        # time.sleep(0.01)
        self.write_icm20948_reg_data(self.ICM20948_INT_PIN_CFG, 0, 0x02) # BYPASS ENABLE
        # time.sleep(0.1)
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00) # I2C_MST_EN set to 0
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x02) # I2C_MST_RST set to 1 (bit auto clears)
        # time.sleep(0.1)
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x01) # clear sleep bit and wake up device
        time.sleep(0.1)


    def i2c_master_init (self):
        # self.write_icm20948_reg_data(self.ICM20948_INT_ENABLE, 0, 0xFF) # enable i2c master interrupt to propagate to interrupt pin1
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x02) # I2C_MST_RST
        # time.sleep(0.1)

        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x20) # When bit 5 set (0x20), the transaction does not write a register value, it will only read data, or write data
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, self.SDP33_i2c_address)

        # self.write_icm20948_reg_data(self.ICM20948_LP_CONFIG, 0, 0x00) #disable master's duty cycled mode
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1


    def i2c_master_write (self, command): # THIS WILL NOT WORK BECAUSE IMU'S MASTER CAPABILITY CAN'T WRITE 2 BYTE COMMAND (ONLY ONE BYTE)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, self.SDP33_i2c_address)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, command >> 8)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, self.SDP33_i2c_address)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, command & 0xFF)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, self.SDP33_i2c_address)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x87) 
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))

    def i2c_master_sdp33_init(self):
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1
        # time.sleep(0.01)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_DO, 3, 0x04)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_REG, 3, 0x31) # adress of the slave register master will write to 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_ADDR, 3, 0x0C) # R/W bit MSB - write operation
        # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0xA9)   # I2C_SLV1_EN, I2C_SLV1_REG_DIS, I2C_SLV1_LENG[3:0] 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0x00)   # I2C_SLV0_DIS

        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_ADDR, 3, 0xA1) # SPD3X i2c address =0x21 | R/W bit MSB - read (1)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0xA9)   # I2C_SLV1_EN, I2C_SLV1_REG_DIS, I2C_SLV1_LENG[3:0] 
        time.sleep(0.1)

        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_REG, 3, 0x00) # adress of the first slave register master will start reading from 
        # print("reading", end = ' ')
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))
        # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV1_CTRL, 3, 0x8f) 

    def i2c_master_mag_init (self):

        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, 0x01) 
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00) # I2C_MST_EN set to 0, I2C_MST_RST set to 1
        # time.sleep(gi)
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 0, I2C_MST_RST set to 1
        # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x02) # I2C_MST_EN set to 0, I2C_MST_RST set to 1
        # time.sleep(0.1)
        

        ## MAGNETOMETER SOFT RESET
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, 0x01) 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG, 3, 0x32) # adress of the slave register master will write to 
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 0x0C) # R/W bit MSB - write operation
        # # time.sleep(gi)
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x8a)   # I2C_SLV0_EN, I2C_SLV0_REG_EN, I2C_SLV0_LENG[3:0] = 9
        # self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x00)   # I2C_SLV0_DIS

        # time.sleep(gi)

        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO, 3, 0x04)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG, 3, 0x31) # adress of the slave register master will write to 
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 0x0C) # R/W bit MSB - write operation
        # time.sleep(gi)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x8a)   # I2C_SLV0_EN, I2C_SLV0_REG_DIS, I2C_SLV0_LENG[3:0] = 9
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x00)   # I2C_SLV0_DIS


        

        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 0x8C) # R/W bit MSB
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG, 3, 0x00) # adress of the first slave register master will start reading from 
        # print("reading", end = ' ')
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))
        # time.sleep(gi)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL, 3, 0x8d)   # I2C_SLV0_EN, I2C_SLV0_REG_EN, I2C_SLV0_LENG[3:0] = 9
        # print(self.read_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR, 3, 1))
        # self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20) # I2C_MST_EN set to 1
        time.sleep(0.1)
        # time.sleep(gi)


    def get_temp(self):
        RoomTemp_Offset = 21
        Temp_Sensitivity = 333.87
        temp_raw_data = self.read_icm20948_reg_data(self.ICM20948_TEMP_OUT_H, 0, 2)
        MSB = temp_raw_data[0]
        LSB = temp_raw_data[1]
        t  = (MSB << 8) + LSB
        TEMP_degC = ((t - RoomTemp_Offset)/Temp_Sensitivity) + 21
        return(TEMP_degC)

    def get_accel_x(self):
        Accel_Sensitivity = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_ACEL_CONFIG, 2, 1) & 0x6))) * 2048)
        accelX_raw_data = self.read_icm20948_reg_data(self.ICM20948_ACEL_XOUT_H, 0, 2)
        accelX = ((accelX_raw_data[0] << 8) + accelX_raw_data[1])
        if accelX > 0x7fff:
            accelX -= 65536
        return(accelX / Accel_Sensitivity)

    def get_accel_y(self):
        Accel_Sensitivity = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_ACEL_CONFIG, 2, 1) & 0x6))) * 2048)
        accelY_raw_data = self.read_icm20948_reg_data(self.ICM20948_ACEL_YOUT_H, 0, 2)
        accelY = ((accelY_raw_data[0] << 8) + accelY_raw_data[1])
        if accelY > 0x7fff:
            accelY -= 65536
        return(accelY / Accel_Sensitivity)

    def get_accel_z(self):
        Accel_Sensitivity = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_ACEL_CONFIG, 2, 1) & 0x6))) * 2048)
        accelZ_raw_data = self.read_icm20948_reg_data(self.ICM20948_ACEL_ZOUT_H, 0, 2)
        accelZ = ((accelZ_raw_data[0] << 8) + accelZ_raw_data[1])
        if accelZ > 0x7fff:
            accelZ -= 65536
        return(accelZ / Accel_Sensitivity)

    ## 131; 65.5; 32,8; 16,4

    def get_gyro_x(self):
        Gyro_Sensitivity = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_GYRO_CONFIG, 2, 1) & 0x6))) * 16.4)
        gyroX_raw_data = self.read_icm20948_reg_data(self.ICM20948_GYRO_XOUT_H, 0, 2)
        gyroX = ((gyroX_raw_data[0] << 8) + gyroX_raw_data[1])
        if gyroX > 0x7fff:
            gyroX -= 65536
        return(gyroX / Gyro_Sensitivity)

    def get_gyro_y(self):
        Gyro_Sensitivity = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_GYRO_CONFIG, 2, 1) & 0x6))) * 16.4)
        gyroY_raw_data = self.read_icm20948_reg_data(self.ICM20948_GYRO_YOUT_H, 0, 2)
        gyroY = ((gyroY_raw_data[0] << 8) + gyroY_raw_data[1])
        if gyroY > 0x7fff:
            gyroY -= 65536
        return(gyroY / Gyro_Sensitivity)

    def get_gyro_z(self):
        Gyro_Sensitivity = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_GYRO_CONFIG, 2, 1) & 0x6))) * 16.4)
        gyroZ_raw_data = self.read_icm20948_reg_data(self.ICM20948_GYRO_ZOUT_H, 0, 2)
        gyroZ = ((gyroZ_raw_data[0] << 8) + gyroZ_raw_data[1])
        if gyroZ > 0x7fff:
            gyroZ -= 65536
        return(gyroZ / Gyro_Sensitivity)

    
    def SDP33_write (self, SDP33_i2c_address, command):
        self.bus.write_i2c_block_data(self.SDP33_i2c_address, command)


    def SDP33_read (self, SDP33_i2c_address, command):
        # write = i2c_msg.write(SDP33_i2c_address, command)
        # read = i2c_msg.read(SDP33_i2c_address, 9)
        
                # raw_data = bus2.i2c_rdwr(write, read)
        self.bus2.write_i2c_block_data(self, self.SDP33_i2c_address, 0, [0x36, 0x24])
        raw_data = self.bus2.read_i2c_block_data(self, self.SDP33_i2c_address, 9)        
        return(raw_data)

    def get_mag(self, cal_available):

        if (cal_available):
            cal_file = open("ICM20948_mag_cal.txt", "r")
            cal_consts = cal_file.readline().split(",")

            offset_x = float(cal_consts[0])
            offset_y = float(cal_consts[1])
            offset_z = float(cal_consts[2])

            scale_x = float(cal_consts[3])
            scale_y = float(cal_consts[4])
            scale_z = float(cal_consts[5])

            # print(str(offset_x)+"\n")
            # print(str(offset_y)+"\n")
            # print(str(offset_z)+"\n")

            # print(str(scale_x)+"\n")
            # print(str(scale_y)+"\n")
            # print(str(scale_z)+"\n")
        else:
            offset_x, offset_y, offset_z = 0, 0, 0
            scale_x, scale_y, scale_z = 1, 1, 1



        mag_raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00, 0, 13)

        magX = (mag_raw_data[6] << 8) + mag_raw_data[5]
        magY = (mag_raw_data[8] << 8) + mag_raw_data[7]
        magZ = (mag_raw_data[10] << 8) + mag_raw_data[9]

        if magX > 0x7fff:
            magX -= 65536
        if magY > 0x7fff:
            magY -= 65536
        if magZ > 0x7fff:
            magZ -= 65536
        
        mag_scf = 4912/32752.0

        # print(magX)
        # print(((magX*mag_scf) - offset_x) * scale_x)

        

        return(((magX*mag_scf) - offset_x) * scale_x, ((magY*mag_scf) - offset_y) * scale_y, ((magZ*mag_scf) - offset_z)*scale_z)

    def calib_mag(self, calib_time):
        try:
            decision = False
            print("\nDo you wish to perform new magnetometer calibration? Old calibration data will be lost!")
            
                
            while not decision:
                start_cal =  raw_input("[Y/N]\n")
                if (start_cal == 'N') or (start_cal == 'n'):
                    print("\nCalibration canceled, no new calibration values saved.\n\n")
                    sys.exit(1)
                elif (start_cal == 'Y') or (start_cal == 'y'):
                    decision = True

            self.i2c_master_mag_init()
            delay = 5
            print("\nStarting calibration in %d seconds with duration of %d seconds!\n" % (delay,calib_time))
            time.sleep(1)
            for i in range(delay):
                print(str(delay-i))
                time.sleep(1)
            
            print("Calibration has started!\n")            

            t_end = time.time() + calib_time
            mag_x = []
            mag_y = []
            mag_z = []

            while time.time() < t_end:
                mag_x_i, mag_y_i, mag_z_i = self.get_mag(False)
                mag_x.append(mag_x_i)
                mag_y.append(mag_y_i)
                mag_z.append(mag_z_i)
                print("%f,%f,%f\n" % (mag_x_i, mag_y_i, mag_z_i))
         

            ### HARDIRON COMPAS COMPENSATION
          
            offset_x = (max(mag_x) + min(mag_x)) / 2
            offset_y = (max(mag_y) + min(mag_y)) / 2
            offset_z = (max(mag_z) + min(mag_z)) / 2

            ### SOFTIRON COMPASS COMPENSATION

            avg_delta_x = (max(mag_x) - min(mag_x)) / 2
            avg_delta_y = (max(mag_y) - min(mag_y)) / 2
            avg_delta_z = (max(mag_z) - min(mag_z)) / 2

            avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3

            scale_x = avg_delta / avg_delta_x
            scale_y = avg_delta / avg_delta_y
            scale_z = avg_delta / avg_delta_z

            # sys.stdout.write(str(offset_x)+"\n")
            # sys.stdout.write(str(offset_y)+"\n")
            # sys.stdout.write(str(offset_z)+"\n")

            # sys.stdout.write(str(scale_x)+"\n")
            # sys.stdout.write(str(scale_y)+"\n")
            # sys.stdout.write(str(scale_z)+"\n")

            decision = False
            print("\nFinished. Do you wish to save calibration data?")
            
            while not decision:
                start_cal =  raw_input("[Y/N]\n")
                if (start_cal == 'N') or (start_cal == 'n'):
                    print("\nCalibration canceled, no new calibration values saved.\n\n")
                    sys.exit(1)
                elif (start_cal == 'Y') or (start_cal == 'y'):
                    decision = True

        except KeyboardInterrupt:
                
            print("\nCalibration canceled, no new calibration values saved.\n\n")
            sys.exit(0)

        cal_file = open("ICM20948_mag_cal.txt", "w")
        cal_file.write("%f,%f,%f,%f,%f,%f" % (offset_x, offset_y, offset_z, scale_x, scale_y, scale_z))
        cal_file.close()

        sys.stdout.write("Calibration successful!\n\n")


