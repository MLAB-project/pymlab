#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class

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
'''
cfg = config.Config(
    i2c = {
        "port": port,
    },

	bus = [
		{
            "type": "i2chub",
            "address": 0x70,
            
            "children": [
                {"name": "mag", "type": "mag01", "gauss": 1.3, "channel": 0, }
            ],
		},
	],
)
'''

cfg = config.Config(
    i2c = {
        "port": port,
    },
    bus = [
        {
            "name":          "mag",
            "type":        "mag01",
            "gauss":        0.88,
        },
    ],
)


cfg.initialize()
mag = cfg.get_device("mag")
sys.stdout.write(" MLAB magnetometer sensor module example \r\n")
time.sleep(0.5)

#### Data Logging ###################################################

sys.stdout.write("Magnetometer data acquisition system started \n")

try:
    while True:
        mag.route()
        (x, y, z) = mag.axes()
        #sys.stdout.write("\rHeading: " + magnetometer.degrees(magnetometer.heading()) + " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " )
        sys.stdout.write(" X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    AZ:" + str(mag.get_azimuth()) + "\r\n")
        sys.stdout.flush()
        time.sleep(0.5)
except KeyboardInterrupt:
	sys.exit(0)
