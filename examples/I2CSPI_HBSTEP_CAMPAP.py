#!/usr/bin/python
# -------------------------------------------
# CAMCAP device controll software
# -------------------------------------------

import sys
import time
from pymlab import config
import ConfigParser

if len(sys.argv) < 2:
    print ""
    print "USING:", sys.argv[0], "[ open | close | toggle]"
    print "-----------"
    print "[CAMCAP]"
    print "open = 0"
    print "-----------"

try:
    cfgfile = ConfigParser.ConfigParser()
    cfgfile.read('CAMCAP.ini')
except Exception, e:
    print "You need config file 'CAMCAP.ini' with containt:"
    print ""



class axis:
    def __init__(self, SPI_CS, Direction, StepsPerUnit):
        ' One axis of robot '
        self.CS = SPI_CS
        self.Dir = Direction
        self.SPU = StepsPerUnit
        self.Reset()

    def Reset(self):
        ' Reset Axis and set default parameters for H-bridge '
        spi.SPI_write_byte(self.CS, 0xC0)      # reset
#        spi.SPI_write_byte(self.CS, 0x14)      # Stall Treshold setup
#        spi.SPI_write_byte(self.CS, 0xFF)  
#        spi.SPI_write_byte(self.CS, 0x13)      # Over Current Treshold setup 
#        spi.SPI_write_byte(self.CS, 0xFF)  
        spi.SPI_write_byte(self.CS, 0x15)      # Full Step speed 
        spi.SPI_write_byte(self.CS, 0xFF)
        spi.SPI_write_byte(self.CS, 0xFF) 
        spi.SPI_write_byte(self.CS, 0x05)      # ACC 
        spi.SPI_write_byte(self.CS, 0x00)
        spi.SPI_write_byte(self.CS, 0x30) 
        spi.SPI_write_byte(self.CS, 0x06)      # DEC 
        spi.SPI_write_byte(self.CS, 0x00)
        spi.SPI_write_byte(self.CS, 0x30) 
        spi.SPI_write_byte(self.CS, 0x0A)      # KVAL_RUN
        spi.SPI_write_byte(self.CS, 0xF0)
        spi.SPI_write_byte(self.CS, 0x0B)      # KVAL_ACC
        spi.SPI_write_byte(self.CS, 0xF0)
        spi.SPI_write_byte(self.CS, 0x0C)      # KVAL_DEC
        spi.SPI_write_byte(self.CS, 0xF0)
        spi.SPI_write_byte(self.CS, 0x18)      # CONFIG
        spi.SPI_write_byte(self.CS, 0b00111000)
        spi.SPI_write_byte(self.CS, 0b00000000)
      
    def MaxSpeed(self, speed):
        ' Setup of maximum speed '
        spi.SPI_write_byte(self.CS, 0x07)       # Max Speed setup 
        spi.SPI_write_byte(self.CS, 0x00)
        spi.SPI_write_byte(self.CS, speed)  

    def ReleaseSW(self):
        ' Go away from Limit Switch '
        while self.ReadStatusBit(2) == 1:           # is Limit Switch ON ?
            spi.SPI_write_byte(self.CS, 0x92 | (~self.Dir & 1))     # release SW 
            while self.IsBusy():
                pass
            self.MoveWait(10)           # move 10 units away
 
    def GoZero(self, speed):
        ' Go to Zero position '
        self.ReleaseSW()

        spi.SPI_write_byte(self.CS, 0x82 | (self.Dir & 1))       # Go to Zero
        spi.SPI_write_byte(self.CS, 0x00)
        spi.SPI_write_byte(self.CS, speed)  
        while self.IsBusy():
            pass
        time.sleep(0.3)
        self.ReleaseSW()

    def Move(self, units):
        ' Move some distance units from current position '
        steps = units * self.SPU  # translate units to steps 
        if steps > 0:                                          # look for direction
            spi.SPI_write_byte(self.CS, 0x40 | (~self.Dir & 1))       
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

    def Float(self):
        ' switch H-bridge to High impedance state '
        spi.SPI_write_byte(self.CS, 0xA0)

    def ReadStatusBit(self, bit):
        ' Report given status bit '
        spi.SPI_write_byte(self.CS, 0x39)   # Read from address 0x19 (STATUS)
        spi.SPI_write_byte(self.CS, 0x00)
        data0 = spi.SPI_read_byte()           # 1st byte
        spi.SPI_write_byte(self.CS, 0x00)
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
        "name":"spi", 
        "type":"i2cspi"
        },
    ],
)
cfg.initialize()

print "Stepper motor control example. \r\n"

spi = cfg.get_device("spi")

spi.route()


try:
    spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)
    time.sleep(0.5)

    X = axis(spi.I2CSPI_SS0, 0, 3000)    # set Number of Steps for open/close
    X.Reset()
    X.MaxSpeed(1)                      # set maximal motor speed 

    if sys.argv[1] == "open":
        if cfgfile.get("CAMCAP", "open")  == '0':
            X.MoveWait(-1)
            cfgfile.set("CAMCAP", "open", '1')
        else:
            print "cap was opened"
    elif sys.argv[1] == "close":
        if cfgfile.get("CAMCAP", "open")  == '1':
            X.MoveWait(1) 
            cfgfile.set("CAMCAP", "open", '0')
        else:
            print "cap was closed"
    elif  sys.argv[1] == "toggle":
        if cfgfile.get("CAMCAP", "open") == '1':
            cfgfile.set("CAMCAP", "open", '0')
            X.MoveWait(1) 
            print "closed"
        elif cfgfile.get("CAMCAP", "open") == '0':
            X.MoveWait(-1) 
            cfgfile.set("CAMCAP", "open", '1')
            print "opened"
    else:
        print "USING:", sys.argv[1], "[ open | close ]"

    with open('CAMCAP.ini', 'w') as file:
        cfgfile.write(file)
    X.Float()   # release power

except KeyboardInterrupt:
    X.Float()   # release power
    sys.stdout.write("\r\n Engine Stopped. \r\n")
    sys.exit(0)

