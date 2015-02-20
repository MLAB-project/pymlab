#!/usr/bin/python

# Python example of use pymlab module to read from MLAB's Melexis thermopile sensor

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
	sys.stderr.write("Usage: %s #I2CPORT\n" % (sys.argv[0], ))
	sys.exit(1)

port    = eval(sys.argv[1])

#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
    },

	bus = [
		{
            "type": "i2chub",
            "address": 0x70,
            
            "children": [
                {"name": "thermopile", "type": "thermopile01", "channel": 0, }
            ],
		},
	],
)


cfg.initialize()

sensor = cfg.get_device("thermopile")
sys.stdout.write(" MLAB Thermopile sensor example \r\n")
time.sleep(0.5)

#### Data Logging ###################################################

sys.stdout.write("Temperature acquisition system started \n")

try:
    sensor.setAddress(0x01); # Default address is 0x5A. Call this function only if your device has different address.
    while True:
       print "Ta ", sensor.getTambient(),  "  To1 ", sensor.getTobject1(), "  To2 ", sensor.getTobject2()
       time.sleep(1)

except KeyboardInterrupt:
	sys.exit(0)
