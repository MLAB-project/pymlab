#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class

import time
import sys

from pymlab import config


#### Script Arguments ###############################################

if len(sys.argv) != 3:
	sys.stderr.write("Invalid number of arguments.\n")
	sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
	sys.exit(1)

port    = eval(sys.argv[1])
address = eval(sys.argv[2])


#### Sensor Configuration ###########################################

cfg = config.Config(
	port = port,
	bus = [
		{
			"name":          "altimet",
			"type":        "altimet01",
			"address":     address,
		},
	],
)
cfg.initialize()

gauge = cfg.get_device("altimet")


#### Data Logging ###################################################

try:
	while True:
		(t, p) = gauge.get_tp()
		sys.stdout.write(" Temperature: " + str(t) + " Pressure: " + str(p) + "\r\n")
		sys.stdout.flush()
		time.sleep(0.5)
except KeyboardInterrupt:
	sys.exit(0)
