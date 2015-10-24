#!/usr/bin/python

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
    #spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)
    spi.GPIO_config(spi.I2CSPI_SS0 | spi.I2CSPI_SS1 |spi.I2CSPI_SS2 | spi.I2CSPI_SS3, 0x50)

    print "SPI blinking.."
    
    while True:
        for x in [0xFE, 0xFD, 0xFB, 0xF7, 0xFB, 0xFD]:
            spi.GPIO_write(x)
            time.sleep(0.1)
finally:
    print "stop"
