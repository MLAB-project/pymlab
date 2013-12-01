#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class

import time
import datetime
import sys

from pymlab import config


#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT \n" % (sys.argv[0], ))
    sys.exit(1)

port    = eval(sys.argv[1])


#### Sensor Configuration ###########################################

cfg = config.Config(
    port = port,
    bus = [
        {
	    	"type": "i2chub",
	    	"address": 0x72,
	   	"children": [
            		{"name": "altimet", "type": "altimet01" , "channel": 6, },
	],
        }, 
    ],
)
cfg.initialize()
gauge = cfg.get_device("altimet")
time.sleep(0.5)


#### Data Logging ###################################################

gauge.route()

try:
    with open("temperature.log", "a") as f:
        while True:
            (t, p) = gauge.get_tp()
            sys.stdout.write(" Temperature: %.2f  Pressure: %d\n" % (t, p, ))
            f.write("%d\t%s\t%.2f\t%d\n" % (time.time(), datetime.datetime.now().isoformat(), t, p, ))
            sys.stdout.flush()
            time.sleep(0.5)
except KeyboardInterrupt:
    sys.exit(0)

