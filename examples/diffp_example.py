#!/usr/bin/python

# Python test script for Sensirion SDP610 sensor used as pitot tube sensor for a small UAV. 

import time
import datetime
import sys
import numpy as np
#import logging 
#logging.basicConfig(level=logging.DEBUG) 


from pymlab import config


#### Script Arguments ###############################################

if len(sys.argv) not in (2, 3):
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT [Config number] \n" % (sys.argv[0], ))
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
                    {"name": "pitot_tube", "type": "SDP600" , "channel": 0, },   
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
                "name":          "pitot_tube",
                "type":        "SDP610",
            },
        ],
    ),
]

try:
    cfg = cfglist[cfg_number]
except IndexError:
    sys.stdout.write("Invalid configuration number.\n")
    sys.exit(1)

cfg.initialize()
gauge = cfg.get_device("pitot_tube")
time.sleep(0.5)

#### Data Logging ###################################################

sys.stdout.write("MLAB pitot-static tube data acquisition system started \n")

gauge.route()

dp = np.array([gauge.get_p()])

try:
        while True:
            gauge.route()
            dp = np.append(dp, gauge.get_p())
            sys.stdout.write("Pressure Diff: %f \n" % np.nanmean(dp))
            sys.stdout.flush()
            time.sleep(0.1)
            
except KeyboardInterrupt:
    sys.exit(0)

