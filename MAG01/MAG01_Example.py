#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class


import time
import sys
import MAG01

MAG01.init()

#     MAG01.hmc5883l(gauss = 4.7, declination = (-2,5))
    (x, y, z) = MAG01.axes()

    while True:
        sys.stdout.write("\rHeading: " + MAG01.heading() + "     ")
	sys.stdout.write("Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n")
        sys.stdout.flush()
        time.sleep(0.5)

