#!/usr/bin/python

#%load_ext autoreload
#%autoreload 2

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
            "device": 'hid'
    },
    bus = [
        {
            "name":          "lighting",
            "type":        "LIGHTNING01A",
        },
    ])
cfg.initialize()

#print "SHT25 humidity and temperature sensor example \r\n"
#print "Temperature  Humidity[%%]  \r\n"
sensor = cfg.get_device("lighting")
time.sleep(0.5)

i=0

#### Data Logging ###################################################

try:
    sensor.setNoiseFloor(0)
    sensor.setIndoor(False)
    sensor.setSpikeRejection(0b0000)
    while True:
        i += 1
        distance = sensor.getDistance()
        print("Storm is {:02d} km away".format(distance))
        print("sINTer:",sensor.getInterrupts())
        print("AFEgai:",sensor.getAFEgain())
        print("power: ", sensor.getPowerStatus())
        print("indoor:", sensor.getIndoor())
        print("Noise noise floor is {} uVrms".format(sensor.getNoiseFloor()))
        print("Spike rejection 0b{:04b}".format(sensor.getSpikeRejection()))
        print("single Energy:", sensor.getSingleEnergy(), bin(sensor.getSingleEnergy()))
        print("Mask dusturbance:", sensor.getMaskDist())

        #sensor.setNoiseFloor(0)
        time.sleep(0.5)
        if i == 10:
            i = 0
            print("=================")
            sensor.setMaskDist(True)

            #sensor.reset()
            #sensor.calib_rco()
except KeyboardInterrupt:
    sys.exit(0)
