#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port    = eval(sys.argv[1])
#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
    },
    bus = [
        {
            "name":        "temp_out",
            "type":        "sht31",
            "address":     0x45,
        },
        {
            "name":        "temp_in",
            "type":        "sht31",
            "address":     0x44,
        },
        {
            "name":        "wind_spd",
            "type":        "rps01",
            "address":     0x40,
        },
        {
            "name":        "wind_dir",
            "type":        "mag01",
            "gauss":       0.88,
            "address":     0x1E,
        },
        {
            "name":        "light",
            "type":        "isl03",
            "address":     0x48,
        },
    ],
)


cfg.initialize()

sen_light = cfg.get_device("light")
sen_tempOut = cfg.get_device("temp_out")
sen_tempIn = cfg.get_device("temp_in")
sen_windSpd = cfg.get_device("wind_spd")
sen_windDir = cfg.get_device("wind_dir")

try:
    sen_tempOut.soft_reset()
    sen_tempIn.soft_reset()
except Exception, e:
    print e

time.sleep(0.5)

try:
    while True:

        try:
            light = sen_light.get_lux()
        except Exception, e:
            print e
            light = "Err"

        try:
            temperatureIn, humidityIn   = sen_tempIn.get_TempHum()
        except Exception, e:
            print e
            temperatureIn = "Err"
            humidityIn = "Err"

        try:
            temperatureOut, humidityOut = sen_tempOut.get_TempHum()
        except Exception, e:
            print e
            temperatureOut = "Err"
            humidityOut = "Err"

        try:
            WindSpeed = sen_windSpd.get_speed()
        except Exception, e:
            print e
            WindSpeed = "Err"

        try:
            (x, y, z) = sen_windDir.axes()

            if y > 0:
                winddirAWS = 90 - (math.atan(x/y))*180.0/math.pi
            elif y < 0:
                winddirAWS = 270 - (math.atan(x/y))*180.0/math.pi
            elif y == 0 & x < 0:
                winddirAWS =  180.0
            elif y == 0 & x > 0:
                winddirAWS = 0.0

        except Exception, e:
            print e
            winddirAWS = "Err"


        try:
            sys.stdout.write("Osvetleni: %s \r\nTemperatureIn: %s, HumidityIn: %s \r\nTemperatureOut: %s, HumidityOut: %s \r\n WindSpeed: %s ,WindDirection: %s \r\n \r\n" %(str(light), str(temperatureIn), str(humidityIn), str(temperatureOut), str(humidityOut), str(WindSpeed), str(winddirAWS)))
            sys.stdout.flush()
        except Exception, e:
            print e

        time.sleep(1)

except KeyboardInterrupt:
    sys.exit(0)

