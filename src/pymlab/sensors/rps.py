#!/usr/bin/python

# Python library for RPS01A MLAB module with magnetic rotary position I2C Sensor
#
import struct
import logging
import numpy as np
import time

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class RPS01(Device):
    """
        MLAB Rotary position sensor I2C driver with AS5048B 
    """

    def __init__(self, parent = None, address = 0x40, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions 
        self.programming_control = 0x03
        self.address_reg = 0x15
        self.zero_position_MSB = 0x16
        self.zero_position_LSB = 0x17
        self.AGC_reg = 0xFA
        self.diagnostics_reg = 0xFB
        self.magnitude_MSB = 0xFC
        self.magnitude_LSB = 0xFD
        self.angle_MSB = 0xFE
        self.angle_LSB = 0xFF

    def get_address(self):
        """ 
            Returns sensors I2C address.
        """
        LOGGER.debug("Reading RPS01A sensor's address.",)
        return self.bus.read_byte_data(self.address, self.address_reg)

    def get_zero_position(self):
        """
        Returns programmed zero position in OTP memory.
        """

        LSB = self.bus.read_byte_data(self.address, self.zero_position_MSB)
        MSB = self.bus.read_byte_data(self.address, self.zero_position_LSB)
        DATA = (MSB << 6) + LSB
        return DATA

    def set_zero_position(self, angle = None):
        self.bus.write_byte_data(self.address, self.zero_position_MSB, 0x00)   # Write 0 to OTP zero position register to clear
        self.bus.write_byte_data(self.address, self.zero_position_LSB, 0x00)

        LSB = self.bus.read_byte_data(self.address, self.angle_LSB)         # Get angle
        MSB = self.bus.read_byte_data(self.address, self.angle_MSB)

        if angle == None:

            status = get_diagnostics()
            if not status['Comp_Low'] or status['Comp_High'] or status['COF']:
                self.bus.write_byte_data(self.address, self.zero_position_MSB, MSB)   # Write previously red data to OTP zero position register
                self.bus.write_byte_data(self.address, self.zero_position_LSB, LSB)            
                return True

            else:
                return  None
        else: 
            raise NotImplementedError()             ## set angle value from function parameter.  Needs to calculate values of LSB and MSB registers.

    def burn_zero_position(self):
            raise NotImplementedError()
 

    def get_agc_value(self):
        """ 
            Returns sensor's Automatic Gain Control actual value.
            0 - Represents high magtetic field 
            0xFF - Represents low magnetic field
        """
        LOGGER.debug("Reading RPS01A sensor's AGC settings",)
        return self.bus.read_byte_data(self.address, self.AGC_reg)

    def get_diagnostics(self):
        """
        Reads diagnostic data from the sensor.
        OCF (Offset Compensation Finished) - logic high indicates the finished Offset Compensation Algorithm. After power up the flag remains always to logic high.

        COF (Cordic Overflow) - logic high indicates an out of range error in the CORDIC part. When this bit is set, the angle and magnitude data is invalid. 
            The absolute output maintains the last valid angular value.

        COMP low, indicates a high magnetic field. It is recommended to monitor in addition the magnitude value.
        COMP high, indicated a weak magnetic field. It is recommended to monitor the magnitude value.
        """

        status = self.bus.read_byte_data(self.address, self.diagnostics_reg)
        bits_values = dict([('OCF',status & 0x01 == 0x01),
                            ('COF',status & 0x02 == 0x02),
                            ('Comp_Low',status & 0x04 == 0x04),
                            ('Comp_High',status & 0x08 == 0x08)])
        return bits_values


    def get_magnitude(self):
        LSB = self.bus.read_byte_data(self.address, self.magnitude_LSB)
        MSB = self.bus.read_byte_data(self.address, self.magnitude_MSB)
        DATA = (MSB << 6) + LSB
        return DATA

    def get_angle(self, verify = False):
        """
        Retuns measured angle in degrees in range 0-360.
        """
        LSB = self.bus.read_byte_data(self.address, self.angle_LSB)
        MSB = self.bus.read_byte_data(self.address, self.angle_MSB)
        DATA = (MSB << 6) + LSB
        if not verify:
            return  (360.0 / 2**14) * DATA
        else:
            status = self.get_diagnostics()
            if not (status['Comp_Low']) and  not(status['Comp_High']) and not(status['COF']):
                return  (360.0 / 2**14) * DATA
            else:
                return  None


    def get_speed(self, multiply = 1, averaging = 50):
        angles = np.zeros(5)
        angles[4] = self.get_angle(verify = False)
        time.sleep(0.01)
        angles[3] = self.get_angle(verify = False)
        time.sleep(0.01)
        angles[2] = self.get_angle(verify = False)
        time.sleep(0.01)
        angles[1] = self.get_angle(verify = False)
        n = 0
        speed = 0
        AVERAGING = averaging

        for i in range(AVERAGING):
            time.sleep(0.01)
            angles[0] = self.get_angle(verify = False)

            if (angles[0] + n*360 - angles[1]) > 300:
                n -= 1
                angles[0] = angles[0] + n*360

            elif (angles[0] + n*360 - angles[1]) < -300:
                n += 1
                angles[0] = angles[0] + n*360

            else:
                angles[0] = angles[0] + n*360

            speed += (-angles[4] + 8*angles[3] - 8*angles[1] + angles[0])/12
            angles = np.roll(angles, 1)

        speed = speed/AVERAGING
        return speed*multiply
