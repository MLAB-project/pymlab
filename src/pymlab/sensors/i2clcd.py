#!/usr/bin/python


import struct
import logging
import time

from pymlab.sensors import Device

LOGGER = logging.getLogger(__name__)

class I2CLCD(Device):
    """
    Example:
    
        # Python library for I2C module with alpha-numeric LCD display

    """

    def __init__(self, parent = None, address = 0x27, fault_queue = 1, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

## register definitions 
        self.backlight = 0b00000000

## config parameters
        self.LCD_RS = 0b00000001
        self.LCD_RW = 0b00000010
        self.LCD_EN = 0b00000100
        self.LCD_BL = 0b00001000


    def initialize(self):
        LOGGER.debug("LCD initialized initialized. ")

    def reset(self):
        self.bus.write_byte(self.address, 0xFF)
        time.sleep(20/1000)
        self.bus.write_byte(self.address, 0x30+self.LCD_EN)
        self.bus.write_byte(self.address, 0x30)
        time.sleep(10/1000)
        self.bus.write_byte(self.address, 0x30+self.LCD_EN)
        self.bus.write_byte(self.address, 0x30)
        time.sleep(1/1000)
        self.bus.write_byte(self.address, 0x30+self.LCD_EN)
        self.bus.write_byte(self.address, 0x30)
        time.sleep(1/1000)
        self.bus.write_byte(self.address, 0x20+self.LCD_EN)
        self.bus.write_byte(self.address, 0x20)
        time.sleep(1/1000)


    def cmd(self, cmd):
        self.bus.write_byte(self.address, (cmd & 0xF0)|self.LCD_EN | self.LCD_BL )
        self.bus.write_byte(self.address, (cmd & 0xF0)  | self.LCD_BL)
        self.bus.write_byte(self.address, ((cmd << 4) & 0xF0)|self.LCD_EN  | self.LCD_BL)
        self.bus.write_byte(self.address, ((cmd << 4) & 0xF0) | self.LCD_BL )
        time.sleep(4/1000)

    def clear(self):
        self.cmd(0x01)
        time.sleep(4/1000)


    def init (self):
        self.reset()
        self.cmd(0x0c)
        self.cmd(0x06)
        self.cmd(0x80)
        self.clear()


    # Function to display single Character
    def lcd_data(self, dat):
        self.bus.write_byte(self.address, ( ord(dat) & 0xF0)| self.LCD_EN | self.LCD_RS | self.LCD_BL)
        self.bus.write_byte(self.address, ( ord(dat) & 0xF0)| self.LCD_RS | self.LCD_BL)
        self.bus.write_byte(self.address, (( ord(dat) << 4) & 0xF0)| self.LCD_EN | self.LCD_RS | (self.LCD_BL))
        self.bus.write_byte(self.address, (( ord(dat) << 4) & 0xF0)| self.LCD_RS | self.LCD_BL)
        time.sleep(4/1000)
        #time.sleep(0.5)


    def puts(self, a):
        for i in list(str(a)):
            self.lcd_data(i) 

    def putsFull(self, lineA = None, lineB = None):
        #self.clear()
        self.home()
        time.sleep(0.01)
        self.clear()
        if lineA:
            time.sleep(0.01)
            self.puts(lineA)
        if lineB:
            time.sleep(0.01)
            self.set_row2()
            time.sleep(0.01)
            self.puts(lineB)

    def set_row2(self):
        self.cmd(0xc0)

    def home(self):
        self.cmd(0x02)
        
    def light(self, on = 0):
        if on:
            self.LCD_BL = 0b00001000
            self.bus.write_byte(self.address, (0 |(self.LCD_BL) ))
        else:
            self.LCD_BL = 0b00000000
            self.bus.write_byte(self.address, (0 &(~self.LCD_BL) ))
        
    def lightToggle(self):
        if self.LCD_BL == 0b00001000:
            self.LCD_BL = 0b00000000
            self.bus.write_byte(self.address, (0 | self.LCD_BL ))
        else:
            self.LCD_BL = 0b00001000
            self.bus.write_byte(self.address, (0 | self.LCD_BL ))
