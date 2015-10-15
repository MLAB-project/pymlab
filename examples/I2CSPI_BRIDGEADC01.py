#!/usr/bin/python

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import sys
import time
from pymlab import config

cfg = config.Config(
    i2c = {
        "port": 8,
    },

    bus = [
        { "name":"spi", "type":"i2cspi"},
    ],
)

cfg.initialize()

print "SPI weight scale sensor with SPI interface. The interface is connected to the I2CSPI module which translates signalls. \r\n"

spi = cfg.get_device("spi")


try:
    print "SPI configuration.."
    spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)
    spi.GPIO_config(spi.I2CSPI_SS2 | spi.I2CSPI_SS3, 0x50)
    #time.sleep(2)


    spi.SPI_write(spi.I2CSPI_SS0, [0x14])       # weight treshold setup 
    spi.SPI_write(spi.I2CSPI_SS0, [0x15])

    spi.SPI_write(spi.I2CSPI_SS0, [0x07])       # weight speed setup 
    spi.SPI_write(spi.I2CSPI_SS0, [0x00])
    spi.SPI_write(spi.I2CSPI_SS0, [0x19])


    while weight < 10:
    

        spi.SPI_write(spi.I2CSPI_SS0, [0x40])       ## wait for desired weight
        spi.SPI_write(spi.I2CSPI_SS0, [0x00])
        spi.SPI_write(spi.I2CSPI_SS0, [0xC8])
        spi.SPI_write(spi.I2CSPI_SS0, [0x00])

        data = spi.SPI_read(1)
        weight = (~(data[0] >> 3)) & 0xF
        
        time.sleep(1)

finally:
    print "weight prepared"

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Future more usable code. 
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

cfg = config.Config(
    i2c = {
        "port": 8,
    },

    bus = [
            {
                "name": "spi",
                "type": "i2cspi",
                "address": 0x2E,
                "GPIO_config": (spi.I2CSPI_SS2 | spi.I2CSPI_SS3, 0x50),
                
                "children": [
                    {"name": "bridgeadc", "type": "bridgeadc01" , "channel": 0, "SPI_config" = (spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)},   
                ],
            },
    ],
)


bridgeadc = cfg.get_device("bridgeadc")


try:

    bridgeadc.Setup_treshold(0x14)       # treshold setup 
    bridgeadc.Setup_max_speed(0x07)       # max measuring speed setup 

    while weight < 10:
    
        weight = bridgeadc.get_weight()       ## wait to defined weight
        time.sleep(1)

finally:
    print "stop"

