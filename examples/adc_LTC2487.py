#!/usr/bin/python

# Python example of use pymlab with LIONCELL01 MLAB module

import time
import sys
from pymlab import config

import logging 
logging.basicConfig(level=logging.DEBUG) 

while True:
    #### Sensor Configuration ###########################################
    cfg = config.Config(
        i2c = {
            "port": 8, # I2C bus number
        },

	    bus = [
                {
                 "name": "adc",
                 "type": "LTC2487", 
                 "address":0x24, 
                },
            ],
    )


    cfg.initialize()
    adc = cfg.get_device("adc")

    Ra = 4700.0     # Circuit Constants optimized for PT100 sensor.  
    Rb = 1500.0
    N = 18

    time.sleep(1)
    try:
        while True:
            for i in range(1,4):
                adc.setADC(channel = 0)
                time.sleep(0.5)
                # Voltage readout
                adc_value = adc.readADC()

                if isinstance(adc_value, (float, int, long)): 
                    Rpt100 = Ra * adc_value /(2**(N-1) - adc_value)
                    Vref = (Ra + Rpt100)/(Ra + Rb + Rpt100)
                    Vpt100 = Vref * adc_value / 2**(N-1)
                    sys.stdout.write("Channel: %d ADC: %d Rpt100: %.2f  Vpt100: %.6f \n" % (i, adc_value, Rpt100, Vpt100))
                    sys.stdout.flush()
                else:
                    print "OUT OF RANGE"

                print adc_value

    except IOError:
        print "IOError"
        continue

    except KeyboardInterrupt:
    	sys.exit(0)
