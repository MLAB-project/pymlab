#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class


import time
import sys
import MAG01

# Example of example use: 
# sudo ./MAG01_Example.py 5

magnetometer = MAG01.mag01(int(sys.argv[1]), gauss = 8.10, declination = (-2,5))

while True:
	(x, y, z) = magnetometer.axes()
#	sys.stdout.write("\rHeading: " + magnetometer.degrees(magnetometer.heading()) + " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " )
	sys.stdout.write(" X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " + "\r\n")
	sys.stdout.flush()
	time.sleep(0.5)


