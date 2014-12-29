#!/usr/bin/python

#uncomment for debbug purposes
import logging
logging.basicConfig(level=logging.DEBUG) 

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

print "SPI barometer sensor reading example. \r\n"

spi = cfg.get_device("spi")

try:
    print "SPI configuration.."
    spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_LEADING| spi.I2CSPI_CLK_461kHz)
    time.sleep(2)

    init0 = [0x88, 0x00, 0x8A, 0x00, 0x8C, 0x00, 0x8E, 0x00]
    init1 = [0x90, 0x00, 0x92, 0x00, 0x94, 0x00, 0x96, 0x00]
    spi.SPI_write(spi.I2CSPI_SS0, init0)              # get all sensor coeficients in one SPI transaction (uses I2CSPI module buffer)
    coefficients0 = spi.SPI_read(8)
    spi.SPI_write(spi.I2CSPI_SS0, init1)              # get all sensor coeficients in one SPI transaction (uses I2CSPI module buffer)
    coefficients1 = spi.SPI_read(8)
    a0 = (coefficients0[1] << 5) + (coefficients0[3] >> 3) + (coefficients0[3] & 0x07)/8.0;
    b1 = ((((coefficients0[5] & 0x1F) * 0x100) + coefficients0[7]) / 8192.0) - 3;
    b2 = ((((coefficients1[1] - 0x80) << 8) + coefficients1[3])/ 16384.0) - 2;
    c12 =(((coefficients1[5] * 0x100) + coefficients1[7])/16777216.0);

    while True:
        print "Sensor inicialization"
        spi.SPI_write(spi.I2CSPI_SS0, [0x24,0x00])
        time.sleep(0.05)
        spi.SPI_write(spi.I2CSPI_SS0, [0x80,0x00,0x82,0x00])
        data = spi.SPI_read(4)
        
        ADC_pressure = ((data[1] << 8) + data[3] ) >> 6;  # conversion of 8bit registers to 16bit variable 
 
        spi.SPI_write(spi.I2CSPI_SS0, [0x84,0x00,0x86,0x00])
        data = spi.SPI_read(4)

        ADC_temperature = ((data[1] << 8) + data[3] ) >> 6;  # conversion of 8bit registers to 16bit variable 
        Pcomp = a0 + (b1 + c12 * ADC_temperature) * ADC_pressure + b2 * ADC_temperature  # compute relative compensated pressure
        pressure_kPa = Pcomp * ((115.0 - 50.0)/1023.0) + 50.0
        sys.stdout.write("Pressure: %.3f kPa \n" % pressure_kPa )
    
        time.sleep(2)

finally:
    print "stop"
