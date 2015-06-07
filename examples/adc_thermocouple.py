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
            # Voltage readout
            x = adc.readADC()
            v = x[0]<<24 | x[1]<<16 | x[2]<<8 | x[3]
            v ^= 0x80000000
            if (x[0] & 0x80)==0:
                v = v - 0xFFFFFFff 
            voltage = float(v)
            voltage = voltage * 1.225 / (2147483648.0)
            voltage += 2e-6
            temperature = voltage / 0.0000397
            print "Voltage =", x, hex(v), voltage, temperature
            time.sleep(1)
            x = adc.readTemp(3)
            v = x[0]<<24 | x[1]<<16 | x[2]<<8 | x[3]
            v ^= 0x80000000
            if (x[0] & 0x80)==0:
                v = v - 0xFFFFFFff 
            voltage = float(v)
            voltage = voltage * 1.225 / (2147483648.0)
            voltage -= 2e-6
            temperature = voltage / 0.0000397
            print "Temperature =", x, hex(v), voltage, temperature
            time.sleep(1)
            x = adc.readADC()
            time.sleep(1)


    except IOError:
        print "IOError"
        continue

    except KeyboardInterrupt:
    	sys.exit(0)
