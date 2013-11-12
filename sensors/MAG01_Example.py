#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class


import time
import sys
import MAG01

magnetometer = MAG01.mag01(8, gauss = 4.7, declination = (-2,5))

while True:
	(x, y, z) = magnetometer.axes()
	sys.stdout.write("\rHeading: " + magnetometer.degrees(magnetometer.heading()) + " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " )
	sys.stdout.flush()
	time.sleep(0.5)


