#!/usr/bin/python

# Python test script for MLAB ALTIMET01A sensor

import time
import datetime
import sys
import logging 
logging.basicConfig(level=logging.DEBUG) 


from pymlab import config


#### Script Arguments ###############################################

if len(sys.argv) not in (2, 3):
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT\n" % (sys.argv[0], ))
    sys.exit(1)

port       = eval(sys.argv[1])
if len(sys.argv) > 2:
    cfg_number = eval(sys.argv[2])
else:
    cfg_number = 0

#### Sensor Configuration ###########################################

cfglist=[
    config.Config(
        i2c = {
            "port": port,
        },

        bus = [
            {
                "type": "i2chub",
                "address": 0x72,
                
                "children": [
                    {"name": "altimet", "type": "altimet01" , "channel": 7, },   
                ],
            },
        ],
    ),
    config.Config(
        i2c = {
            "port": port,
        },
        bus = [
            {
                "name":          "altimet",
                "type":        "altimet01",
            },
        ],
    ),
]

try:
    cfg = cfglist[cfg_number]
except IndexError:
    sys.stdout.write("Invalid configuration number.")
    sys.exit(1)

cfg.initialize()
gauge = cfg.get_device("altimet")
time.sleep(0.5)

#### Data Logging ###################################################

sys.stdout.write("ALTIMET data acquisition system started \n")

try:
        while True:
            gauge.route()
            (t1, p1) = gauge.get_tp()
            sys.stdout.write(" Temperature: %.2f  Pressure: %d \n" % (t1, p1))
            sys.stdout.flush()
            time.sleep(0.5)
            
except KeyboardInterrupt:
    sys.exit(0)

