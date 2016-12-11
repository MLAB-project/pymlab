#!/usr/bin/python

# Python library for RPS01A MLAB module with AS5048B I2C Magnetic position sensor.

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
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port    = eval(sys.argv[1])
#### Sensor Configuration ###########################################

''''
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
            "name":          "encoder",
            "type":        "rps01",
        },
    ],
)


cfg.initialize()

print "RPS01A magnetic position sensor RPS01 readout example \r\n"
sensor = cfg.get_device("encoder")

print sensor.get_address()
print sensor.get_zero_position() 

#### Data Logging ###################################################

try:
    while True:
        sys.stdout.write("RPS01A Angle: " + str(sensor.get_angle(verify = False)) + "\tSpeed: " + str(sensor.get_speed()) + "\r\n")
        sys.stdout.flush()
        time.sleep(0.1)
except KeyboardInterrupt:
    sys.exit(0)
