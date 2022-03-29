#!/usr/bin/python

# Python library for SHT3101A MLAB module with SHT31 Temperature and relative humidity sensor.

import time, datetime
import sys
from pymlab import config
from __init__ import auto_int, loggerArgparse
from __init__ import InfluxLogger as MongoLogger

#### Script Arguments ###############################################

parser = loggerArgparse(description = "SHT3x driver")
parser.add_argument('--period', help='Delay between two samples, [s]', type=float, default = 0.25)
parser.add_argument('--name', help='Sensor data indentificator', type=str, default = "HYGRO01")

args = vars(parser.parse_args())

logger = MongoLogger(sensor_type = "SHT3x", sensor = args['name'])

print(args)
#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": args['bus'],
        "device": args['driver'],
    },
    bus = [
        {
            "name":      "sht",
            "type":      "sht31",
            "address":    args['address'],
        },
    ],
)


cfg.initialize()

print ("SHT31 sensor readout example \r\n")
sensor = cfg.get_device("sht")

#sensor.soft_reset()
time.sleep(0.1)

#### Data Logging ###################################################

try:
    while True:
        temperature, humidity = sensor.get_periodic_measurement()
        data = {"temp": temperature, "hum": humidity}
        print(data)
        logger.insert_data(data)
        print("Temp: %0.2f, Hum: %0.2f\r\n" % (temperature, humidity))
        sys.stdout.flush()
        time.sleep(args['period'])

except KeyboardInterrupt:
    sys.exit(0)
