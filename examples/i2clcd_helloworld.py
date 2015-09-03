#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

#uncomment for debbug purposes
import logging
logging.basicConfig(level=logging.DEBUG) 

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
address = 0x27
#### Sensor Configuration ###########################################
'''
cfg = config.Config(
    i2c = {
        "port": port,
    },

    bus = [
        {
            "type": "i2chub",
            "address": 0x72,
            
            "children": [
                {"name": "lcd", "type": "i2clcd", "address": address, "channel": 1, }
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
            "name":          "lcd",
            "type":        "i2clcd",
            "address":        address,
        },
    ],
)



cfg.initialize()
lcd = cfg.get_device("lcd")
lcd.reset()
lcd.init()
n = 0

#### Data Logging ###################################################

try:
    while True:
       # sys.stdout.write("print on LCD")
       # sys.stdout.flush()
        lcd.light(1)
        time.sleep(1)
        lcd.light(0)
        time.sleep(1)
        lcd.puts("ahoj")
        n = n+1
        if n == 3:
        #    lcd.cmd(0x01)
        #    lcd.cmd(0x80)
            n = 0
except KeyboardInterrupt:
    sys.exit(0)
