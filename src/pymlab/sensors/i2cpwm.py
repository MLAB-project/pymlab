#!/usr/bin/python

import time

from pymlab.sensors import Device

#TODO: set only one pin, not all bus

class I2CPWM(Device):
    'Python library for I2CPWM01A MLAB module with NXP Semiconductors PCA9531 I2C-bus LED dimmer'

    def __init__(self, parent = None, address = 0b1100011, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.PWM_INPUT = 0x00
        self.PWM_PSC0 = 0x01
        self.PWM_PWM0 = 0x02
        self.PWM_PSC1 = 0x03
        self.PWM_PWM1 = 0x04
        self.PWM_LS0 = 0x05
        self.PWM_LS1 = 0x06


    def set_pwm0(self, frequency, duty): # frequency in Hz, Duty in % (0-100)
        period = int((1.0/float(frequency))*152.0)-1
	duty = int((float(duty)/100.0)*255.0)
        self.bus.write_byte_data(self.address, 0x01, period)
        self.bus.write_byte_data(self.address, self.PWM_PWM0, duty)


    def set_pwm1(self, frequency, duty): # frequency in Hz, Duty in % (0-100)
        period = int((1.0/float(frequency))*152.0)-1
	duty = int((float(duty)/100.0)*255.0)
        self.bus.write_byte_data(self.address, self.PWM_PSC1, period)
        self.bus.write_byte_data(self.address, self.PWM_PWM1, duty)


    def set_ls0(self, mode):
        self.bus.write_byte_data(self.address, self.PWM_LS0, mode)


    def set_ls1(self, mode):
        self.bus.write_byte_data(self.address, self.PWM_LS1, mode)
	

    def get_input(self):
	return self.bus.read_byte_data(self.address, self.PWM_INPUT)


def main():
    print __doc__


if __name__ == "__main__":
    main()
