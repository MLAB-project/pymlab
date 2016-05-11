#!/usr/bin/python

'''
I2C->SPI LED Blinker Example

Connect LEDs to #SS0, #SS1, #SS2 and #SS3
''' 

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import sys
import time
from pymlab import config

cfg = config.Config(
    i2c = {
        "port": 1,
    },

    bus = [
        {
            "type": "i2chub",
            "address": 0x70,
            "children": [
                { "name":"spi", "type":"i2cspi", "channel": 1, },
            ],
        },
    ],
)


cfg.initialize()

print "I2C/SPI example. \r\n"

spi = cfg.get_device("spi")

spi.route()

try:
    print "SPI configuration.."
    spi.GPIO_config(spi.I2CSPI_SS0 | spi.I2CSPI_SS1 |spi.I2CSPI_SS2 | spi.I2CSPI_SS3, 0x50)

    print "SPI blinking.."
    
    while True:
        for x in [0xFE, 0xFD, 0xFB, 0xF7, 0xFB, 0xFD]:
            spi.GPIO_write(x)
            time.sleep(0.1)
finally:
    print "stop"
