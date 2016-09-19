#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 


import time
import datetime
import sys

from pymlab import config

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import math


app=pg.QtGui.QApplication([])

w = gl.GLViewWidget()

zgrid = gl.GLGridItem()

zgrid.rotate(90, 1, 0, 0) # y

zgrid.scale(10, 10, 10)

w.addItem(zgrid)


cloudList = np.array([[0,0],[0,0],[0,0]])
pts1 = np.array([[0,0],[0,0],[0,0]]).transpose()

vect = gl.GLLinePlotItem(pos = pts1, width = 2)
vectx = gl.GLLinePlotItem(pos = pts1, width = 1)
vecty = gl.GLLinePlotItem(pos = pts1, width = 1)
vectz = gl.GLLinePlotItem(pos = pts1, width = 1)

cloud = gl.GLScatterPlotItem()

w.addItem(vect)
w.addItem(vectx)
w.addItem(vecty)
w.addItem(vectz)
w.addItem(cloud)

w.show()

#pg.QtGui.QApplication.exec_()



#### Script Arguments ###############################################

if len(sys.argv) != 2:
	sys.stderr.write("Invalid number of arguments.\n")
	sys.stderr.write("Usage: %s #I2CPORT\n" % (sys.argv[0], ))
	sys.exit(1)

port    = eval(sys.argv[1])

#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
    },
    bus = [
        {
            "name":          "mag",
            "type":        "mag01",
            "gauss":        0.88,
        },
    ],
)


cfg.initialize()
mag = cfg.get_device("mag")
sys.stdout.write(" MLAB magnetometer sensor module example \r\n")
time.sleep(0.5)

#### Data Logging ###################################################

sys.stdout.write("Magnetometer data acquisition system started \n")
def update():
    global vect, vectx, vecty, vectz, cloud, cloudList, x_min, x_max, y_min, y_max, z_min, z_max
    (x, y, z) = mag.axes()


    x = x -150
    z = z -90


    sys.stdout.write(" X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " + "\r\n")
    sys.stdout.flush()
    pts = np.array([[0,x],[0,y],[0,z]]).transpose()
    vect.setData(pos=pts)
    
    pts = np.array([[0,x],[0,0],[0,0]]).transpose()
    vectx.setData(pos=pts)
    
    pts = np.array([[0,0],[0,y],[0,0]]).transpose()
    vecty.setData(pos=pts)
    
    pts = np.array([[0,0],[0,0],[0,z]]).transpose()
    vectz.setData(pos=pts)
    
    cloudList = np.append(cloudList, [[x],[y],[z]], axis=1)
    cloud.setData(pos=cloudList.transpose())

    if y > 0:
        headind1 = 90 - (math.atan(x/y))*180.0/math.pi
    elif y < 0:
        headind1 = 270 - (math.atan(x/y))*180.0/math.pi
    elif y == 0 & x < 0:
        headind1 =  180.0
    elif y == 0 & x > 0:
        headind1 = 0.0

    if z > 0:
        headind2 = 90 - (math.atan(y/z))*180.0/math.pi
    elif z < 0:
        headind2 = 270 - (math.atan(y/z))*180.0/math.pi
    elif z == 0 & y < 0:
        headind2 = 180.0
    elif z == 0 & y > 0:
        headind2 = 0.0

    if x > 0:
        headind3 = 90 - (math.atan(z/x))*180.0/math.pi
    elif x < 0:
        headind3 = 270 - (math.atan(z/x))*180.0/math.pi
    elif x == 0 & z < 0:
        headind3 = 180.0
    elif x == 0 & z > 0:
        headind3 = 0.0

    print headind1, headind2, headind3




t = QtCore.QTimer()
t.timeout.connect(update)
t.start(100)
pg.QtGui.QApplication.exec_()
