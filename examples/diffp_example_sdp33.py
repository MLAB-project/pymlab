#!/usr/bin/python

# Python test script for Sensirion SDP610 sensor used as pitot tube sensor for a small UAV. 

import time
import datetime
import sys
import numpy as np
import os

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
            "device": "smbus",
        },
        bus = [
            {
                "name":        "pitot_tube",
                "type":        "SDP33",
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

log_name = ("SDP33_tp_log_%s.txt" % datetime.datetime.utcfromtimestamp(time.time()).isoformat())
# filepath = "/home/jakub/SDP33_logs/" + log_name
filepath = "SDP33_logs/" + log_name
log_file = open(filepath, "w")
# log_file = open(log_name, "w")

sys.stdout.write("MLAB pitot-static tube data acquisition system started \n")

gauge.route()
gauge.reset()
gauge.start_meas()

num = 0


while True:

    try:
            
        gauge.route()

        dp, t ,dbg_rd0,dbg_rd1, dbg_rd2, dbg_rd3, dbg_rd4, dbg_rd5, dbg_rd6, dbg_rd7, dbg_rd8 = gauge.get_tp()
        ts = time.time()
        msg = ("%d;%0.4f;%0.2f;%0.3f;%d;%d;%d;%d;%d;%d;%d;%d;%d\n"% (num, ts, dp, t, dbg_rd0,dbg_rd1, dbg_rd2, dbg_rd3, dbg_rd4, dbg_rd5, dbg_rd6, dbg_rd7, dbg_rd8))
        log_file.write(msg)
        

        if num % (25) == 0 :
            sys.stdout.write("%d; %0.3f; Pressure Diff: %+4.2f [Pa]; Temp %2.3f [degC];%d;%d;%d;%d;%d;%d;%d;%d;%d\n" % (num, ts, dp, t,dbg_rd0,dbg_rd1, dbg_rd2, dbg_rd3, dbg_rd4, dbg_rd5, dbg_rd6, dbg_rd7, dbg_rd8))
        # sys.stdout.flush()
            # sys.stdout.write(msg)
            # sys.stdout.flush()

        num += 1
        
        # time.sleep(0.5)
                
    except KeyboardInterrupt:
        sys.exit(0)

    # except IOError:
    #         sys.stdout.write("\r\n************ I2C Error\r\n")
    #         time.sleep(1)
    #         gauge.reset()
    #         gauge.start_meas()

