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

print "SPI barometer sensor reading example. \r\n"

spi = cfg.get_device("spi")

spi.route()




print "SPI configuration.."
spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_1843kHz)
spi.GPIO_config(spi.I2CSPI_SS2 | spi.I2CSPI_SS3, 0x50)
#time.sleep(2)
print "Driver inicialization"
spi.SPI_write_byte(spi.I2CSPI_SS0, 0xC0)

#for i in range(2):
#    for x in [0xFE, 0xFD, 0xFB, 0xF7, 0xFB, 0xFD]:
#        spi.GPIO_write(x)
#        time.sleep(0.05)


#spi.SPI_write_byte(spi.I2CSPI_SS0, 0x14)       # stall treshold setup 
#spi.SPI_write_byte(spi.I2CSPI_SS0, 0x15)  

spi.SPI_write_byte(spi.I2CSPI_SS0, 0x07)       # max speed setup 
spi.SPI_write_byte(spi.I2CSPI_SS0, 0x00)
spi.SPI_write_byte(spi.I2CSPI_SS0, 0x19)  

time.sleep(0.2)

while True:
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0x41)       ## run to defined step position
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0x00)  
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0xC8)  
    #spi.SPI_write_byte(spi.I2CSPI_SS0, [0x40,0x00,0x55,0])  
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0x10)  


    #spi.SPI_write_byte(spi.I2CSPI_SS0, [0x40, 0x00, 0xC8, 0x00] )       ## run to defined step position
    #spi.SPI_write_byte(0xF4, [0xF7] )       ## run to defined step position

    for n in range(300):
        spi.SPI_write_byte(spi.I2CSPI_SS0, 0x39)
        spi.SPI_write_byte(spi.I2CSPI_SS0, 0)
        spi.SPI_write_byte(spi.I2CSPI_SS0, 0)
        #print map(hex, spi.SPI_read_byte())
        print hex(spi.SPI_read_byte())

    print '**************************************************************************8'

    spi.SPI_write_byte(spi.I2CSPI_SS0, 0x40 )       ## run to defined step position
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0x00)  
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0xC8)  
    #spi.SPI_write_byte(spi.I2CSPI_SS0, [0x40,0x00,0x55,0])  
    spi.SPI_write_byte(spi.I2CSPI_SS0, 0x10)  


    #spi.SPI_write_byte(spi.I2CSPI_SS0, [0x40, 0x00, 0xC8, 0x00] )       ## run to defined step position
    #spi.SPI_write_byte(0xF4, [0xF7] )       ## run to defined step position

    for n in range(300):
        spi.SPI_write_byte(spi.I2CSPI_SS0, 0x39)
        spi.SPI_write_byte(spi.I2CSPI_SS0, 0)
        spi.SPI_write_byte(spi.I2CSPI_SS0, 0)
        #print map(hex, spi.SPI_read_byte())
        print hex(spi.SPI_read_byte())
        
    print '**************************************************************************8'



