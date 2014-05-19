#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class
# This code is adopted from: 

import math
import time
import sys
import logging

from pymlab.sensors import Device


LOGGER = logging.getLogger(__name__)

class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class IMU01_ACC(Device):
    """
    Example:
    
    """

    def __init__(self, parent = None, address = 0x1C, g_range = 4.0, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self._gauss = gauss
        (reg, self._scale) = self.SCALES[gauss]

        self.MMA_845XQ_CTRL_REG1    = 0x2A
        self.MMA_845XQ_CTRL_REG1_VALUE_ACTIVE = 0x01
        self.MMA_845XQ_CTRL_REG1_VALUE_F_READ = 0x02

        self.MMA_845XQ_CTRL_REG2 = 0x2B
        self.MMA_845XQ_CTRL_REG2_RESET = 0x40

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


    def initialize(self):
        reg, self._scale = self.SCALES[self._gauss]
        self.bus.read_byte(self.address)
        self.bus.write_byte_data(self.address, self.HMC5883L_CRA, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, self.HMC5883L_CRB, reg << 5) # Scale
        self.bus.write_byte_data(self.address, self.HMC5883L_MR, 0x00) # Continuous measurement
        LOGGER.debug("Byte data %s to register %s to address %s writen",
            bin(self.bus.read_byte_data(self.address, self.HMC5883L_MR)), hex(self.HMC5883L_MR), hex(self.address))


    def standby(self):
        Wire.beginTransmission(_addr); // Set to status reg
        Wire.write((uint8_t)MMA_845XQ_CTRL_REG1);
        Wire.endTransmission();
  
        Wire.requestFrom((uint8_t)_addr, (uint8_t)1);
        if (Wire.available())
        {
            reg1 = Wire.read();
        }
        Wire.beginTransmission(_addr); // Reset
        Wire.write((uint8_t)MMA_845XQ_CTRL_REG1);
        Wire.write(reg1 & ~MMA_845XQ_CTRL_REG1_VALUE_ACTIVE);

    def active(self):
        uint8_t reg1 = 0x00;
        Wire.beginTransmission(_addr); // Set to status reg
        Wire.write((uint8_t)MMA_845XQ_CTRL_REG1);
        Wire.endTransmission();
  
        Wire.requestFrom((uint8_t)_addr, (uint8_t)1);
        if (Wire.available())
        {
            reg1 = Wire.read();
        }
        Wire.beginTransmission(_addr); // Reset
        Wire.write((uint8_t)MMA_845XQ_CTRL_REG1);
        Wire.write(reg1 | MMA_845XQ_CTRL_REG1_VALUE_ACTIVE | (_highres ? 0 : MMA_845XQ_CTRL_REG1_VALUE_F_READ) | 0x38);
        Wire.endTransmission();

    def begin(bool highres, uint8_t scale):
          _highres = highres;
          
          _scale = scale;
          _step_factor = (_highres ? 0.0039 : 0.0156); // Base value at 2g setting
          if( _scale == 4 )
            _step_factor *= 2;
          else if (_scale == 8)
            _step_factor *= 4;
          uint8_t wai = _read_register(0x0D); // Get Who Am I from the device.
          // return value for MMA8543Q is 0x3A
          
          Wire.beginTransmission(_addr); // Reset
          Wire.write(MMA_845XQ_CTRL_REG2);
          Wire.write(MMA_845XQ_CTRL_REG2_RESET);
          Wire.endTransmission();
          delay(10); // Give it time to do the reset
          _standby();
          Wire.beginTransmission(_addr); // Set Portrait/Landscape mode
          Wire.write(MMA_845XQ_PL_CFG);
          Wire.write(0x80 | MMA_845XQ_PL_EN);
          Wire.endTransmission();
          Wire.beginTransmission(_addr);
          Wire.write(MMA_845XQ_XYZ_DATA_CFG);
          if (_scale == 4 || _scale == 8)
            Wire.write((_scale == 4) ? MMA_845XQ_4G_MODE : MMA_845XQ_8G_MODE);
          else // Default to 2g mode
            Wire.write((uint8_t)MMA_845XQ_2G_MODE);
          Wire.endTransmission();
          _active();

    def getPLStatus(self):
        return _read_register(MMA_845XQ_PL_STATUS);

    def getPulse():
        _write_register(MMA_845XQ_PULSE_CFG, MMA_845XQ_PULSE_CFG_ELE);
        return (_read_register(MMA_845XQ_PULSE_SRC) & MMA_845XQ_PULSE_SRC_EA);


    def update():
        write_byte(self.address, 0x00)
  
      Wire.requestFrom((uint8_t)_addr, (uint8_t)(_highres ? 7 : 4));
      if (Wire.available())

        _stat = Wire.read();
        if(_highres)

          rx = (int16_t)((Wire.read() << 8) + Wire.read());
          _xg = (rx / 64) * _step_factor;
          ry = (int16_t)((Wire.read() << 8) + Wire.read());
          _yg = (ry / 64) * _step_factor;
          rz = (int16_t)((Wire.read() << 8) + Wire.read());
          _zg = (rz / 64) * _step_factor;

        else
          _xg = (int8_t)Wire.read()*_step_factor;
          _yg = (int8_t)Wire.read()*_step_factor;
          _zg = (int8_t)Wire.read()*_step_factor;

    def setInterrupt(uint8_t type, uint8_t pin, bool on)
        uint8_t current_value = _read_register(0x2D);

        if(on)
        current_value |= type;
        else
        current_value &= ~(type);

        _write_register(0x2D, current_value);

        uint8_t current_routing_value = _read_register(0x2E);

        if (pin == 1)
        current_routing_value &= ~(type);

        else if (pin == 2)
        current_routing_value |= type;

        _write_register(0x2E, current_routing_value);

    def disableAllInterrupts(self):
        self.bus.write_byte_data(self.address, 0x2D, 0)

