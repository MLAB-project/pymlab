#!/usr/bin/python


#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT\n" % (sys.argv[0], ))
    sys.exit(1)

port    = sys.argv[1]
#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
        "device": 'smbus',  # Now it works only with SMBus driver
    },
	bus = []
)


bus = cfg.initialize()
print(bus)
print(type(bus))

driver = bus.get_driver()

print(driver)
print(type(driver))
#help(driver)

dev = bus.driver.scan_bus(verbose = True)
try:
    print(dev)
except KeyboardInterrupt:
    sys.exit(0)
