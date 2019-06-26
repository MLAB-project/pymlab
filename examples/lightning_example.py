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
            "port": 0
    },
    bus = [
        {
            "name":          "lighting",
            "type":        "LIGHTNING01A",
        },
    ])
cfg.initialize()

sensor = cfg.get_device("lighting")

time.sleep(0.5)
#sensor.reset()

print("Start Antenna tunnig.")
sensor.antennatune_on(FDIV=0,TUN_CAP=0)
time.sleep(5)
sensor.reset()

#time.sleep(0.5)

sensor.calib_rco()

time.sleep(0.5)
sensor.reset()

sensor.setWDTH(1)
sensor.setNoiseFloor(1)
#sensor.setIndoor(False)
sensor.setSpikeRejection(0)

time.sleep(0.5)


i=0

#### Data Logging ###################################################

try:
    while True:
        interrupts = sensor.getInterrupts()

        if not any( value == False for value in interrupts):

            print("sINTer:", interrupts, i)
            print("WDTH:",sensor.getWDTH())
    #        print("power: ", sensor.getPowerStatus())
            print("indoor:", sensor.getIndoor())
            print("Noise floor is {} uVrms".format(sensor.getNoiseFloor()))
            print("Spike rejection 0b{:04b}".format(sensor.getSpikeRejection()))
            print("single Energy:", sensor.getSingleEnergy(), bin(sensor.getSingleEnergy()))
            print("Mask disturbance:", sensor.getMaskDist())
            print("Storm is {:02d} km away".format(sensor.getDistance()))

            time.sleep(0.5)

            i += 1 

        else:
            time.sleep(5)

except KeyboardInterrupt:
    sys.exit(0)
