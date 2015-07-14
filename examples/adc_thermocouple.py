#!/usr/bin/python

# Python example of use pymlab with LIONCELL01 MLAB module

import time
import sys
from pymlab import config

while True:
    #### Sensor Configuration ###########################################
    cfg = config.Config(
        i2c = {
            "port": 0, # I2C bus number
        },

	    bus = [
                {
                 "name": "adc",
                 "type": "i2cadc01", 
                 #"channel": 7, 
                },
            ],
    )


    cfg.initialize()
    adc = cfg.get_device("adc")

    try:
        while True:
            # Temperature readout
            temperature = adc.readTemp()
            print "Internal Temperature =", float("{0:.2f}".format(temperature))

            time.sleep(3)

            # Voltage readout
            voltage = adc.readADC()
            temp = (voltage / 0.0000397) + temperature   #temperrature calculation for K type thermocouple
            print "Voltage =", float("{0:.2f}".format(voltage)), ",  K-type thermocouple Temperature =", float("{0:.2f}".format(temp))

            time.sleep(3)

    except IOError:
        print "IOError"
        continue

    except KeyboardInterrupt:
    	sys.exit(0)
