#!/usr/bin/python
# -------------------------------------------
# HBSTEP01A Stepper Motor control Example
# -------------------------------------------

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import sys
import time
from pymlab import config


class axis:
    def __init__(self, SPI_CS, Direction, StepsPerUnit):
        ' One axis of robot '
        self.CS = SPI_CS
        self.Dir = Direction
        self.SPU = StepsPerUnit
        self.Reset()

    def Reset(self):
        ' Reset Axis and set default parameters for H-bridge '
        spi.SPI_write(self.CS, [0xC0, 0x60])      # reset
#        spi.SPI_write(self.CS, [0x14, 0x14])      # Stall Treshold setup
#        spi.SPI_write(self.CS, [0xFF, 0xFF])  
#        spi.SPI_write(self.CS, [0x13, 0x13])      # Over Current Treshold setup 
#        spi.SPI_write(self.CS, [0xFF, 0xFF])  
        spi.SPI_write(self.CS, [0x15, 0xFF])      # Full Step speed 
        spi.SPI_write(self.CS, [0xFF, 0xFF])
        spi.SPI_write(self.CS, [0xFF, 0xFF]) 
        spi.SPI_write(self.CS, [0x05, 0x05])      # ACC 
        spi.SPI_write(self.CS, [0x00, 0x00])
        spi.SPI_write(self.CS, [0x75, 0x75]) 
        spi.SPI_write(self.CS, [0x06, 0x06])      # DEC 
        spi.SPI_write(self.CS, [0x00, 0x00])
        spi.SPI_write(self.CS, [0x75, 0x75]) 
        spi.SPI_write(self.CS, [0x0A, 0x0A])      # KVAL_RUN
        spi.SPI_write(self.CS, [0x10, 0x10])
        spi.SPI_write(self.CS, [0x0B, 0x0B])      # KVAL_ACC
        spi.SPI_write(self.CS, [0x10, 0x10])
        spi.SPI_write(self.CS, [0x0C, 0x0C])      # KVAL_DEC
        spi.SPI_write(self.CS, [0x10, 0x10])
        spi.SPI_write(self.CS, [0x18, 0x18])      # CONFIG
        spi.SPI_write(self.CS, [0b00111000, 0b00111000])
        spi.SPI_write(self.CS, [0b00000000, 0b00000000])
      
    def MaxSpeed(self, speed):
        ' Setup of maximum speed '
        spi.SPI_write(self.CS, [0x07, 0x07])       # Max Speed setup 
        spi.SPI_write(self.CS, [0x00, 0x00])
        spi.SPI_write(self.CS, [speed, speed])  

    def ReleaseSW(self):
        ' Go away from Limit Switch '
        while self.ReadStatusBit(2) == 1:           # is Limit Switch ON ?
            spi.SPI_write(self.CS, [0x92, 0x92] | (~self.Dir & 1))     # release SW 
            while self.IsBusy():
                pass
            self.MoveWait(10)           # move 10 units away
 
    def GoZero(self, speed):
        ' Go to Zero position '
        self.ReleaseSW()

        spi.SPI_write(self.CS, [0x82, 0x82] | (self.Dir & 1))       # Go to Zero
        spi.SPI_write(self.CS, [0x00, 0x00])
        spi.SPI_write(self.CS, [speed, speed])  
        while self.IsBusy():
            pass
        time.sleep(0.3)
        self.ReleaseSW()

    def Move(self, units):
        ' Move some distance units from current position '
        steps = units * self.SPU  # translate units to steps 
        if steps > 0:                                          # look for direction
            spi.SPI_write(self.CS, [0x40 | (~self.Dir & 1), 0x40 | (~self.Dir & 1)])       
        else:
            spi.SPI_write(self.CS, [0x40 | (self.Dir & 1), 0x40 | (self.Dir & 1)]) 
        steps = int(abs(steps))     
        spi.SPI_write(self.CS, [(steps >> 16) & 0xFF, (steps >> 16) & 0xFF])
        spi.SPI_write(self.CS, [(steps >> 8) & 0xFF, (steps >> 8) & 0xFF])
        spi.SPI_write(self.CS, [steps & 0xFF, steps & 0xFF])

    def MoveWait(self, units):
        ' Move some distance units from current position and wait for execution '
        self.Move(units)
        while self.IsBusy():
            pass

    def Float(self):
        ' switch H-bridge to High impedance state '
        spi.SPI_write(self.CS, [0xA0, 0xA0])

    def ReadStatusBit(self, bit):
        ' Report given status bit '
        spi.SPI_write(self.CS, [0x39, 0x39])   # Read from address 0x19 (STATUS)
        spi.SPI_write(self.CS, [0x00, 0x00])
        data0 = spi.SPI_read_byte()           # 1st byte
        spi.SPI_write(self.CS, [0x00, 0x00])
        data1 = spi.SPI_read_byte()           # 2nd byte
        #print hex(data0), hex(data1)
        if bit > 7:                                   # extract requested bit
            OutputBit = (data0 >> (bit - 8)) & 1
        else:
            OutputBit = (data1 >> bit) & 1        
        return OutputBit

    
    def IsBusy(self):
        """ Return True if tehre are motion """
        if self.ReadStatusBit(1) == 1:
            return False
        else:
            return True

# End Class axis --------------------------------------------------



cfg = config.Config(
    i2c = {
        "port": 1,
    },

    bus = [
        {
            "type": "i2chub",
            "address": 0x70,
            "children": [
                { "name":"spi", "type":"i2cspi", "channel": 1, },
            ],
        },
    ],
)


cfg.initialize()

print "Stepper motor control example. \r\n"

spi = cfg.get_device("spi")

spi.route()

try:
    print "SPI configuration.."
    spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_58kHz)
    time.sleep(1)

    print "Axis inicialization"
    X = axis(spi.I2CSPI_SS0, 0, 641)    # set Number of Steps per axis Unit and set Direction of Rotation
    X.MaxSpeed(52)                      # set maximal motor speed 

    print "Axis is running"

    for i in range(5):
        X.MoveWait(150)      # move 50 unit forward and wait for motor stop
#        time.sleep(0.5)
        X.MoveWait(-150)     # move 50 unit backward and wait for motor stop
#        time.sleep(0.5)

    X.Float()   # release power

finally:
    print "stop"
