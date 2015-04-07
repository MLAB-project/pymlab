#!/usr/bin/python

# Python library for RPS01A MLAB module with AS5048B I2C Magnetic position sensor.

#uncomment for debbug purposes
import logging
logging.basicConfig(level=logging.DEBUG) 

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
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
            "address": 0x72,
            
            "children": [
                {"name": "encoder", "type": "rps01", "channel": 1, }
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
            "name":          "lts01",
            "type":        "lts01",
            "address":        address,
        },
    ],
)
'''


cfg.initialize()

print "RPS01A magnetic position sensor module example \r\n"
print "Angle [deg] \r\n"
sensor = cfg.get_device("encoder")

#### Data Logging ###################################################

try:
    while True:
        sys.stdout.write("RPS01A Angle:" + str(sensor.get_agc()) + "\r\n")
        sys.stdout.flush()
        time.sleep(0.5)
except KeyboardInterrupt:
    sys.exit(0)
