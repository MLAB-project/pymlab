#!/usr/bin/python

import time

from pymlab.sensors import Device

#TODO: set only one pin, not all bus

class I2CPWM(Device):
    'Python library for I2CPWM01A MLAB module with NXP Semiconductors PCA9531 I2C-bus LED dimmer'

    MODES = {
        'X':       0b00,
        'LOW':     0b01,
        'PWM0':    0b10,
        'PWM1':    0b11,
    }

    def __init__(self, parent = None, address = 0b1100011, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        'The INPUT register reflects the state of the device pins. Writes to this register will be acknowledged but will have no effect.'
        self.PWM_INPUT = 0x00
        'PSC0 is used to program the period of the PWM output.'
        self.PWM_PSC0 = 0x01
        'The PWM0 register determines the duty cycle of BLINK0. The outputs are LOW (LED on) when the count is less than the value in PWM0 and HIGH (LED off) when it is greater. If PWM0 is programmed with 00h, then the PWM0 output is always HIGH (LED off).'
        self.PWM_PWM0 = 0x02
        'PSC1 is used to program the period of the PWM output.'
        self.PWM_PSC1 = 0x03
        'The PWM1 register determines the duty cycle of BLINK1. The outputs are LOW (LED on) when the count is less than the value in PWM1 and HIGH (LED off) when it is greater. If PWM1 is programmed with 00h, then the PWM1 output is always HIGH (LED off).'
        self.PWM_PWM1 = 0x04
        'The LSn LED select registers determine the source of the LED data.'
        self.PWM_LS0 = 0x05
        self.PWM_LS1 = 0x06


    def set_pwm0(self, frequency, duty): # frequency in Hz, Duty cycle in % (0-100)
        period = int((1.0/float(frequency))*152.0)-1
        duty = int((float(duty)/100.0)*255.0)
        self.bus.write_byte_data(self.address, 0x01, period)
        self.bus.write_byte_data(self.address, self.PWM_PWM0, duty)


    def set_pwm1(self, frequency, duty): # frequency in Hz, Duty cycle in % (0-100)
        period = int((1.0/float(frequency))*152.0)-1
        duty = int((float(duty)/100.0)*255.0)
        self.bus.write_byte_data(self.address, self.PWM_PSC1, period)
        self.bus.write_byte_data(self.address, self.PWM_PWM1, duty)


    def set_ls0(self, mode):
        self.bus.write_byte_data(self.address, self.PWM_LS0, mode)


    def set_ls1(self, mode):
        self.bus.write_byte_data(self.address, self.PWM_LS1, mode)

    def set_output_type(self, mode = ['X','X','X','X','X','X','X','X']):
        set_ls0((MODES[mode[0]] << 6) | (MODES[mode[1]] << 4) | (MODES[mode[2]] << 2) | MODES[mode[3]])
        set_ls1((MODES[mode[4]] << 6) | (MODES[mode[5]] << 4) | (MODES[mode[6]] << 2) | MODES[mode[7]])

    def get_input(self):
        return self.bus.read_byte_data(self.address, self.PWM_INPUT)


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
