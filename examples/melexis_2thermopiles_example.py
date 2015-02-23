#!/usr/bin/python

# Python example of use pymlab with thermopile sensor a triacs module for heating

import time
import datetime
import sys

from pymlab import config

import hid

err = 0

while True:

    print "START"

    #### Sensor Configuration ###########################################
    cfg = config.Config(
        i2c = {
            "port": 0, # I2C bus number
        },

	    bus = [
		    {
                "type": "i2chub",
                "address": 0x73,
                
                "children": [
                    {"name": "thermopile1", "type": "thermopile01", "channel": 7, },
                    {"name": "thermopile2", "type": "thermopile01", "channel": 4, },
                ],
		    },
	    ],
    )


    cfg.initialize()
    sensor1 = cfg.get_device("thermopile1")
    sensor2 = cfg.get_device("thermopile2")

    try:
        while True:

            #sensor.setAddress(0x5A);
            sensor1.route()
            print "1  Ta ", sensor1.getTambient(),  "  To1 ", sensor1.getTobject1(), "  To2 ", sensor1.getTobject2(),
            #time.sleep(0.2)
            #sensor.setAddress(0x02);
            sensor2.route()
            print "   2  Ta ", sensor2.getTambient(),  "  To1 ", sensor2.getTobject1(), "  To2 ", sensor2.getTobject2(), err
            #time.sleep(0.2)
    except IOError:
        err = err + 1
        print "IOError"
        continue

    except KeyboardInterrupt:
    	sys.exit(0)
