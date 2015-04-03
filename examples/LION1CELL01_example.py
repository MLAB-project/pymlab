#!/usr/bin/python

# Python example of use pymlab with LIONCELL01 MLAB module

import time
import sys
from pymlab import config

while True:
    #### Sensor Configuration ############################################
    cfg = config.Config(
        i2c = {
            "port": 0, # I2C bus number
        },

	    bus = [
		    {
                "type": "i2chub",
                "address": 0x73,
                
                "children": [
                    {"name": "guage", "type": "lion1cell01", "channel": 7, },
                ],
		    },
	    ],
    )


    cfg.initialize()
    guage = cfg.get_device("guage")

    try:
        while True:
            # Battery status readout
            print "Temp =", guage.getTemp(), "degC, RemainCapacity =", guage.getRemainingCapacity(), "mAh, cap =", guage.FullChargeCapacity(), "mAh, U =", guage.Voltage(), "mV, I =", guage.AverageCurrent(), "mA, charge =", guage.StateOfCharge(), "%"
            time.sleep(3)


    except IOError:
        err = err + 1
        print "IOError"
        continue

    except KeyboardInterrupt:
    	sys.exit(0)
