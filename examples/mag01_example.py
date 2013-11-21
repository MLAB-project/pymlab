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
			"name":          "mag",
			"type":        "mag01",
			"address":     address,
			"gauss":           8.1,
			"declination": (-2, 5),
		},
	],
)
cfg.initialize()

mag = cfg.get_device("mag")


#### Data Logging ###################################################

try:
	while True:
		(x, y, z) = mag.axes()
		#sys.stdout.write("\rHeading: " + magnetometer.degrees(magnetometer.heading()) + " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " )
		sys.stdout.write(" X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " + "\r\n")
		sys.stdout.flush()
		time.sleep(0.5)
except KeyboardInterrupt:
	sys.exit(0)
