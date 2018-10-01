#!/usr/bin/python


#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 3:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port    = sys.argv[1]
address = int(sys.argv[2],0)
#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
        "device": None,  # here you can explicitly set I2C driver with 'hid', 'smbus', 'serial'
        "serial_number": None,
    },

	bus = [
		{
           "name": "rtc01",
           "type": "rtc01",
           "address": address
        }
	]
)


cfg.initialize()

print "counter module example \r\n"

counter = cfg.get_device("rtc01")

#### Data Logging ###################################################


counter.set_config(counter.FUNCT_MODE_count)
counter.reset_counter()

try:
    while True:
        count = counter.get_count()
        print ">>", count
        print counter.get_frequency()
        time.sleep(0.5)
except KeyboardInterrupt:
    sys.exit(0)
