#!/usr/bin/python

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT\n" % (sys.argv[0], ))
    sys.exit(1)

port    = sys.argv[1]
address = 0x50
#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
        "device": None,  # OPTIONAL here you can explicitly set I2C driver with 'hid', 'smbus', 'serial'
        "serial_number": None, # OPTIONAL serial number of I2CUSB01A (CP2112 IO), works only with HID driver
    },
	bus = [
		{
           "name": "rtc01",
           "type": "rtc01",
           "address": address
        }
	]
)


cfg.initialize()

print "counter module example \r\n"

counter = cfg.get_device("rtc01")

#### Data readout ###################################################

counter.set_config(counter.FUNCT_MODE_32)
counter.set_datetime() # if no argument passed, it use UTC sytem datetime

try:
    while True:
        date = counter.get_datetime()
        print int(time.time()), "time", date
        time.sleep(0.5)

except KeyboardInterrupt:
    sys.exit(0)
