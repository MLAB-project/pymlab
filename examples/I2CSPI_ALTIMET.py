#!/usr/bin/python

#uncomment for debbug purposes
import logging
logging.basicConfig(level=logging.DEBUG) 


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

print "SPI barometer sensor reading example. \r\n"

spi = cfg.get_device("spi")


def MPL_init():

    #spi.SPI_write(spi.I2CSPI_SS0, [0x8800, 0x8A00, 0x8C00, 0x8E00, 0x9000, 0x9200, 0x9400, 0x9600])              # get all sensor coeficients in one SPI transaction (uses I2CSPI module buffer)
    spi.SPI_write(spi.I2CSPI_SS0, [0x88, 0x8A, 0x8C, 0x8E, 0x90, 0x92, 0x94, 0x96])              # get all sensor coeficients in one SPI transaction (uses I2CSPI module buffer)
    #coefficients = spi.SPI_read();

 ## translate to floating point number

    #print coefficients
    return
#    a0 = ((unsigned int16) a0_MSB << 5) + (a0_LSB >> 3) + (a0_LSB & 0x07)/8.0;
#    b1 = ((((b1_MSB & 0x1F) * 0x100) + b1_LSB) / 8192.0) - 3;
#    b2 = ((((unsigned int16) (b2_MSB - 0x80) << 8) + b2_LSB)/ 16384.0) - 2;
#    c12 =(((c12_MSB * 0x100) + c12_LSB)/16777216.0);



try:
    print "SPI configuration.."
    print bin(spi.SPI_config(spi.I2CSPI_LSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_LEADING| spi.I2CSPI_CLK_115kHz))
    time.sleep(2)
    
    n=0
    while True:
        print "Sensor inicialization"
        #MPL_init()
        #spi.SPI_write(spi.I2CSPI_SS0, [0x55,0xaa,0x55,0xaa,0x55,0xaa,0x55,0xaa])
        data = [0x51,0x53,0x57,n]
        length = len(data)
        spi.SPI_write(spi.I2CSPI_SS0, data)
        n=n+1
        response = spi.SPI_read(length)
        print "read ", map(hex,response)
        time.sleep(2)

finally:
    print "stop"
