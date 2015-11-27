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
    def __init__(self, spi, SPI_CS, Direction, StepsPerUnit):
        ' One axis of robot '
        self.spi = spi
        self.CS = SPI_CS
        self.Dir = Direction
        self.SPU = StepsPerUnit
        self.Reset()

    def Reset(self):
        ' Reset Axis and set default parameters for H-bridge '
        self.spi.SPI_write_byte(self.CS, 0xC0)      # reset
        self.spi.SPI_write_byte(self.CS, 0x14)      # Stall Treshold setup
        self.spi.SPI_write_byte(self.CS, 0x7F)  
        self.spi.SPI_write_byte(self.CS, 0x14)      # Over Current Treshold setup 
        self.spi.SPI_write_byte(self.CS, 0x0F)  
        #self.spi.SPI_write_byte(self.CS, 0x15)      # Full Step speed 
        #self.spi.SPI_write_byte(self.CS, 0x00)
        #self.spi.SPI_write_byte(self.CS, 0x30) 
        #self.spi.SPI_write_byte(self.CS, 0x0A)      # KVAL_RUN
        #self.spi.SPI_write_byte(self.CS, 0x50)
      
    def MaxSpeed(self, speed):
        ' Setup of maximum speed '
        self.spi.SPI_write_byte(self.CS, 0x07)       # Max Speed setup 
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)  
      
    def ACC(self, speed):
        ' Setup of speed profile acceleration '
        self.spi.SPI_write_byte(self.CS, 0x05)       # Max Speed setup 
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)
    
    def DCC(self, speed):
        ' Setup of speed profile deceleration '
        self.spi.SPI_write_byte(self.CS, 0x06)       # Max Speed setup 
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)

    def ReleaseSW(self):
        ' Go away from Limit Switch '
        while self.ReadStatusBit(2) == 1:           # is Limit Switch ON ?
            self.spi.SPI_write_byte(self.CS, 0x92 | (~self.Dir & 1))     # release SW 
            while self.IsBusy():
                pass
            self.MoveWait(10)           # move 10 units away
 
    def GoZero(self, speed):
        ' Go to Zero position '
        self.ReleaseSW()

        self.spi.SPI_write_byte(self.CS, 0x82 | (self.Dir & 1))       # Go to Zero
        self.spi.SPI_write_byte(self.CS, 0x00)
        self.spi.SPI_write_byte(self.CS, speed)  
        while self.IsBusy():
            pass
        time.sleep(0.3)
        self.ReleaseSW()

    def Move(self, units):
        ' Move some distance units from current position '
        steps = units * self.SPU  # translate units to steps 
        if steps > 0:                                          # look for direction
            self.spi.SPI_write_byte(self.CS, 0x40 | (~self.Dir & 1))
        else:
            spi.SPI_write_byte(self.CS, 0x40 | (self.Dir & 1)) 
        steps = int(abs(steps))     
        spi.SPI_write_byte(self.CS, (steps >> 16) & 0xFF)
        spi.SPI_write_byte(self.CS, (steps >> 8) & 0xFF)
        spi.SPI_write_byte(self.CS, steps & 0xFF)

    def MoveWait(self, units):
        ' Move some distance units from current position and wait for execution '
        self.Move(units)
        while self.IsBusy():
            pass

    def Run(self, spd):
        ' The Run command produces a motion at SPD speed '
        if spd > 0:                                          # look for direction
            self.spi.SPI_write_byte(self.CS, 0x50 | (self.Dir & 1))
        else:
            self.spi.SPI_write_byte(self.CS, 0x51 | (self.Dir & 1))
            spd = spd *-1
        print spd  
        self.spi.SPI_write_byte(self.CS, (spd >> 16) & 0xFF)
        self.spi.SPI_write_byte(self.CS, (spd >>  8) & 0xFF)
        self.spi.SPI_write_byte(self.CS, (spd >>  0) & 0xFF)

    def Float(self):
        ' switch H-bridge to High impedance state '
        self.spi.SPI_write_byte(self.CS, 0xA0)

    def ReadStatusBit(self, bit):
        ' Report given status bit '
        self.spi.SPI_write_byte(self.CS, 0x39)   # Read from address 0x19 (STATUS)
        self.spi.SPI_write_byte(self.CS, 0x00)
        data0 = self.spi.SPI_read_byte()           # 1st byte
        self.spi.SPI_write_byte(self.CS, 0x00)
        data1 = self.spi.SPI_read_byte()           # 2nd byte
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

'''
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
'''

cfg = config.Config(
    i2c = {
        "port": 1,
    },
    bus = [
        { "name":"spi", "type":"i2cspi"},
    ],
)


cfg.initialize()

print "Stepper motor control example. \r\n"

spi = cfg.get_device("spi")

spi.route()

try:
    print "SPI configuration.."
    spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)
    time.sleep(1)

    print "Axis inicialization"
    X = axis(spi, spi.I2CSPI_SS0, 0, 641)    # set Number of Steps per axis Unit and set Direction of Rotation
    X.MaxSpeed(20)                      # set maximal motor speed 

    print "Axis is running"

    for i in range(5):
        X.MoveWait(50)      # move 50 unit forward and wait for motor stop
        time.sleep(0.5)
        X.MoveWait(-50)     # move 50 unit backward and wait for motor stop
        time.sleep(0.5)

    X.Float()   # release power


finally:
    print "stop"
