#!/usr/bin/python

# Python library for SHT3101A MLAB module with SHT31 Temperature and relative humidity sensor.

import time, datetime
import sys
from pymlab import config
from __init__ import auto_int, loggerArgparse
from __init__ import InfluxLogger as MongoLogger

#### Script Arguments ###############################################

parser = loggerArgparse(description = "SEN5x driver")
parser.add_argument('--period', help='Delay between two samples, [s]', type=float, default = 0.25)
parser.add_argument('--name', help='Sensor data indentificator', type=str, default = "AIRBORNEPARTICLES01")

args = vars(parser.parse_args())

logger = MongoLogger(sensor_type = "SEN5x", sensor = args['name'])

print(args)
#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": args['bus'],
        "device": args['driver'],
    },
    bus = [
        {
            "name":      "sen5x",
            "type":      "SEN5x",
            "address":    args['address'],
        },
    ],
)


cfg.initialize()

print ("Sensirion SEN5x sensor readout example \r\n")
sensor = cfg.get_device("sen5x")

print("Cekam minutu na ustaleni senzoru")
sensor.reset()
time.sleep(120)

#### Data Logging ###################################################

try:
    while True:
        data = sensor.get_data(wait=True)
        #print(data)
        logger.insert_data(data)
        time.sleep(args['period'])

except KeyboardInterrupt:
    sys.exit(0)
