#!/usr/bin/python

import time
import sys
import logging

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)


class Gpio(Device):
    def __init__(self, parent = None, address = 0x01, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

    def setup(self, pin, direction = 0b0, push_pull = 0b0):
        raise NotImplementedError()

    def output(self, pin, value):
        raise NotImplementedError()

    def setup_bus(self, bus, direction, push_pull):
        raise NotImplementedError()

    def output_bus(self, bus, value):
        raise NotImplementedError()


class PCA9635(Device):
    """
Python library for PCA9635
    """
    def __init__(self, parent = None, address = 0x01, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions
        self.MODE1 = 0x00
        self.MODE2 = 0x01
        self.LEDOUT0 = 0x14
        self.LEDOUT1 = 0x15
        self.LEDOUT2 = 0x16
        self.LEDOUT3 = 0x17
        self.PWM00 = 0x02
        self.PWM01 = 0x03
        self.PWM02 = 0x04
        self.PWM03 = 0x05
        self.PWM04 = 0x06
        self.PWM05 = 0x07
        self.PWM06 = 0x08
        self.PWM07 = 0x09
        self.PWM08 = 0x0A
        self.PWM09 = 0x0B
        self.PWM10 = 0x0C
        self.PWM11 = 0x0D
        self.PWM12 = 0x0E
        self.PWM13 = 0x0F
        self.PWM14 = 0x10
        self.PWM15 = 0x11

## config parameters
        self.led00_config = (0xAA)
        self.led01_config = (0xAA)
        self.mode1_config = (0x00)
        self.mode2_config = (0x01)

    def get_mode1(self):
        DATA = self.bus.read_byte_data(self.address, self.MODE1)
        Ecal = 1 * DATA
        return Ecal

    def get_mode2(self):
        DATA = self.bus.read_byte_data(self.address, self.MODE2)
        Ecal = 1 * DATA
        return Ecal

    def get_pwm00 (self):
        DATA = self.bus.read_byte_data(self.address, self.PWM00 )
        Ecal = 1 * DATA
        return Ecal

    def get_ledout0(self):
        DATA = self.bus.read_byte_data(self.address, self.LEDOUT0)
        Ecal = 1 * DATA
        return Ecal


    def config(self):
        self.bus.write_byte_data(self.address, self.LEDOUT0, self.led00_config)
        self.bus.write_byte_data(self.address, self.LEDOUT1, self.led01_config)

        self.bus.write_byte_data(self.address, self.MODE1, self.mode1_config)
        self.bus.write_byte_data(self.address, self.MODE2, self.mode2_config)
        return


    def pwm00_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM00, value)
        return

    def pwm01_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM01, value)
        return

    def pwm02_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM02, value)
        return

    def pwm03_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM03, value)
        return

    def pwm04_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM04, value)
        return

    def pwm05_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM05, value)
        return

    def pwm06_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM06, value)
        return

    def pwm07_set(self, value):
        self.bus.write_byte_data(self.address, self.PWM07, value)
        return


class I2CIO_TCA9535(Device):
    'Python library for I2CIO01A MLAB module with Texas Instruments TCA9535 I/O expander'

    def __init__(self, parent = None, address = 0x27, **kwargs):
        Device.__init__(self, parent, address, **kwargs)
        'The Input Port registers (registers 0 and 1) reflect the incoming logic levels of the pins, regardless of whether thepin is defined as an input or an output by the Configuration Register. It only acts on read operation. Writes to these registers have no effect. The default value, X, is determined by the externally applied logic level. Before a read operation, a write transmission is sent with the command byte to let the I 2 C device know that the Input Port registers will be accessed next.'
        self.INPUT_PORT0 = 0x00
        self.INPUT_PORT1 = 0x01

        'The Output Port registers (registers 2 and 3) show the outgoing logic levels of the pins defined as outputs by the Configuration register. Bit values in this register have no effect on pins defined as inputs. In turn, reads from this register reflect the value that is in the flip-flop controlling the output selection, not the actual pin value.'
        self.OUTPUT_PORT0 = 0x02
        self.OUTPUT_PORT1 = 0x03

        'The Polarity Inversion registers (registers 4 and 5) allow polarity inversion of pins defined as inputs by the Configuration register. If a bit in this register is set (written with 1), the corresponding pins polarity is inverted. If a bit in this register is cleared (written with a 0), the corresponding pins original polarity is retained.'
        self.POLARITY_PORT0 = 0x04
        self.POLARITY_PORT1 = 0x05

        'The Configuration registers (registers 6 and 7) configure the directions of the I/O pins. If a bit in this register is set to 1, the corresponding port pin is enabled as an input with a high-impedance output driver. If a bit in this register is cleared to 0, the corresponding port pin is enabled as an output.'
        self.CONTROL_PORT0 = 0x06
        self.CONTROL_PORT1 = 0x07

    def set_polarity(self, port0 = 0x00, port1 = 0x00):
        self.bus.write_byte_data(self.address, self.POLARITY_PORT0, port0)
        self.bus.write_byte_data(self.address, self.POLARITY_PORT1, port1)
        return True #self.bus.read_byte_data(self.address, self.POLARITY_PORT0), self.bus.read_byte_data(self.address, self.PULLUP_PORT1)

    def config_ports(self, port0 = 0x00, port1 = 0x00):
        self.bus.write_byte_data(self.address, self.CONTROL_PORT0, port0)
        self.bus.write_byte_data(self.address, self.CONTROL_PORT1, port1)
        return True

    def set_ports(self, port0 = 0x00, port1 = 0x00):
        'Writes specified value to the pins defined as output by config_ports() method. Writing to input pins has no effect.'
        self.bus.write_byte_data(self.address, self.OUTPUT_PORT0, port0)
        self.bus.write_byte_data(self.address, self.OUTPUT_PORT1, port1)
        return True

    def get_ports(self):
        'Reads logical values at pins.'
        return (self.bus.read_byte_data(self.address, self.STATUS_PORT0), self.bus.read_byte_data(self.address, self.STATUS_PORT1));


class TCA6416A(Device):
    'Python library for I2CIO01A MLAB module with Texas Instruments  TCA6416A I/O expander'

    def __init__(self, parent = None, address = 0x21, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.STATUS_PORT0 = 0x00
        self.STATUS_PORT1 = 0x01

        self.OUTPUT_PORT0 = 0x02
        self.OUTPUT_PORT1 = 0x03

        self.POLARITY_PORT0 = 0x04
        self.POLARITY_PORT1 = 0x05

        self.CONTROL_PORT0 = 0x06
        self.CONTROL_PORT1 = 0x07

    def set_polarity(self, port0 = 0x00, port1 = 0x00):
        self.bus.write_byte_data(self.address, self.POLARITY_PORT0, port0)
        self.bus.write_byte_data(self.address, self.POLARITY_PORT1, port1)
        return #self.bus.read_byte_data(self.address, self.POLARITY_PORT0), self.bus.read_byte_data(self.address, self.PULLUP_PORT1)

    def config_ports(self, port0 = 0x00, port1 = 0x00):
        self.bus.write_byte_data(self.address, self.CONTROL_PORT0, port0)
        self.bus.write_byte_data(self.address, self.CONTROL_PORT1, port1)
        return

    def set_ports(self, port0 = 0x00, port1 = 0x00):
        self.bus.write_byte_data(self.address, self.OUTPUT_PORT0, port0)
        self.bus.write_byte_data(self.address, self.OUTPUT_PORT1, port1)
        return

    def get_ports(self):
        'Reads logical values at pins.'
        return (self.bus.read_byte_data(self.address, self.STATUS_PORT0), self.bus.read_byte_data(self.address, self.STATUS_PORT1));

    def get_config(self):
        'Reads logical values at pins.'
        return (self.bus.read_byte_data(self.address, self.CONTROL_PORT0), self.bus.read_byte_data(self.address, self.CONTROL_PORT1));


class DS4520(Device):
    'Python library for Dallas DS4520 I/O expander'

    def __init__(self, parent = None, address = 0x50, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        """
I/O control for I/O_0 to I/O_7. I/O_0 is the LSB and I/O_7 is the MSB. Clearing
the corresponding bit of the register pulls the selected I/O pin low; setting the
bit places the pulldown transistor into a high-impedance state. When the
pulldown is high impedance, the output floats if no pullup/down is connected
to the pin"""
        self.CONTROL_PORT0 = 0xF2
        self.CONTROL_PORT1 = 0xF3

        'Pullup enable for I/O_8. I/O_8 is the LSB. Only the LSB is used. Set the LSB bit to enable the pullup on I/O_8; clear the LSB to disable the pullup'
        self.PULLUP_PORT0 = 0xF0
        self.PULLUP_PORT1 = 0xF1

        'I/O status for I/O_0 to I/O_7. I/O_0 is the LSB and I/O_7 is the MSB. Writing to this register has no effect. Read this register to determine the state of the I/O_0 to I/O_7 pins.'
        self.STATUS_PORT0 = 0xF8
        self.STATUS_PORT1 = 0xF9

    def set_pullups(self, port0 = 0x00, port1 = 0x00):
        'Sets INPUT (1) or OUTPUT (0) direction on pins. Inversion setting is applicable for input pins  1-inverted 0-noninverted input polarity.'
        self.bus.write_byte_data(self.address, self.PULLUP_PORT0, port0)
        self.bus.write_byte_data(self.address, self.PULLUP_PORT1, port1)
        return #self.bus.read_byte_data(self.address, self.PULLUP_PORT0), self.bus.read_byte_data(self.address, self.PULLUP_PORT1)

    def set_ports(self, port0 = 0x00, port1 = 0x00):
        'Writes specified value to the pins defined as output by method. Writing to input pins has no effect.'
        self.bus.write_byte_data(self.address, self.CONTROL_PORT0, port0)
        self.bus.write_byte_data(self.address, self.CONTROL_PORT0, port1)
        return

    def get_ports(self):
        'Reads logical values at pins.'
        return self.bus.read_byte_data(self.address, self.STATUS_PORT0), self.bus.read_byte_data(self.address, self.STATUS_PORT1);





class USBI2C_GPIO(Gpio):
    IN = 0b0
    OUT = 0b1
    OPEN_DRAIN = 0b0
    PUSH_PULL = 0b1
    SPECIAL_ALL = 0b11100000
    SPECIAL_LED = 0b11000000
    SPECIAL_CLK = 0b00100000
    SPECIAL_OFF = 0b00000000
    PIN_COUNT = 8

    def __init__(self, parent = None, **kwargs):
        Gpio.__init__(self, parent, None, **kwargs)

    def initialize(self):
        print(self.bus.driver.__class__)
        if not self.bus.driver.__class__.__name__ == 'HIDDriver':
            raise ValueError("This {!r} GPIO device requires a 'HIDdriver' driver.".format(self.name))

        self.g_direction = self.bus.driver.gpio_direction
        self.g_pushpull =  self.bus.driver.gpio_pushpull
        self.g_special  =  self.bus.driver.gpio_special
        self.g_clockdiv =  self.bus.driver.gpio_clockdiv


    def update_gpio(self):
        return self.bus.driver.write_hid([0x02, self.g_direction, self.g_pushpull, self.g_special, self.g_clockdiv])

    def setup(self, pin, direction = 0b0, push_pull = 0b0):
        if not (-1 < pin < self.PIN_COUNT):
            raise ValueError("GPIO pin (%i) is out or range [0,7]." %pin)

        if direction: self.g_direction = (self.g_direction | (1<<pin))
        else: self.g_direction = (self.g_direction & ~(1<<pin))

        if push_pull:  self.g_pushpull = (self.g_pushpull | (1<<pin))
        else: self.g_pushpull = (self.g_pushpull & ~(1<<pin))

        self.update_gpio()

    def output(self, pin, value):
        #TODO: Overeni, jestli pin je nastaven jakou output a nasledne udelat chybu
        #  a jestli se nezapisuje na 'special pin'
        if False:
            raise ValueError("Pin is not set as OUTput.")
        self.bus.driver.write_hid([0x04, (bool(value)<<pin), (1 << pin)])

    def set_special(self, special = None, divider = None):
        if special: self.g_special = special
        if divider: self.g_clockdiv = divider

        self.update_gpio()

    #def blick(self, pin, count, delay = None, on = None, off = None):


def main():
    print(__doc__)

if __name__ == "__main__":
    main()
