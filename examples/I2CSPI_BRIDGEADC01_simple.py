#!/usr/bin/python

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 

import sys
import time
from pymlab import config
import logging

"""
Show data from BRIDGEADC01 module. 
"""

##from vispy import app, scene, color

import numpy as np

LOGGER = logging.getLogger(__name__)

    

    
class BRIDGEADC01:
    """
    Driver for the AD7730/AD7730L bridge ADC device. 
    """

    def __init__(self, SPI_CS):

        self.CS = SPI_CS
        #AD7730 register address
        self.AD7730_COMM_REG            =0b000
        self.AD7730_STATUS_REG          =0b000
        self.AD7730_DATA_REG            =0b001
        self.AD7730_MODE_REG            =0b010
        self.AD7730_FILTER_REG          =0b011
        self.AD7730_DAC_REG             =0b100
        self.AD7730_OFFSET_REG          =0b101
        self.AD7730_GAIN_REG            =0b110
        self.AD7730_TEST_REG            =0b111      # do not change state of this register

        self.AD7730_IDLE_MODE           =0b000
        self.AD7730_CCONVERSION_MODE    =0b001
        self.AD7730_SCONVERSION_MODE    =0b010
        self.AD7730_POWERDOWN_MODE      =0b011
        self.AD7730_INT_ZERO_CALIBRATION=0b100
        self.AD7730_INT_FULL_CALIBRATION=0b101
        self.AD7730_SYSTEM_ZERO_CALIBRATION=0b110
        self.AD7730_SYSTEM_FULL_CALIBRATION=0b111

        self.AD7730_UNIPOLAR_MODE        =0b0
        self.AD7730_UNIPOLAR_MODE       =0b1
        self.AD7730_IOENABLE_MODE       =0b1
        self.AD7730_IODISABLE_MODE      =0b0
        self.AD7730_16bitDATA_MODE      =0b0
        self.AD7730_24bitDATA_MODE      =0b1
        self.AD7730_REFERENCE_2V5       =0b0        
        self.AD7730_REFERENCE_5V        =0b1
        self.AD7730_10mVIR_MODE         =0b00
        self.AD7730_20mVIR_MODE         =0b01
        self.AD7730_40mVIR_MODE         =0b10
        self.AD7730_80mVIR_MODE         =0b11
        self.AD7730_MCLK_ENABLE_MODE    =0b0
        self.AD7730_MCLK_DISABLE_MODE   =0b1
        self.AD7730_BURNOUT_DISABLE     =0b0
        self.AD7730_BURNOUT_ENABLE      =0b1
        self.AD7730_AIN1P_AIN1N         =0b00
        self.AD7730_AIN2P_AIN2N         =0b01
        self.AD7730_AIN1N_AIN1N         =0b10
        self.AD7730_AIN1N_AIN2N         =0b11      

    def reset(self):
        spi.SPI_write(self.CS, [0xFF])       # wrinting least 32 serial clock with 1 at data input resets the device. 
        spi.SPI_write(self.CS, [0xFF])
        spi.SPI_write(self.CS, [0xFF])
        spi.SPI_write(self.CS, [0xFF])

    def single_write(self, register, value):
        comm_reg = (0b00000 << 3) + register
        spi.SPI_write(self.CS, [comm_reg] + value)

    def single_read(self, register):
        '''
        Reads data from desired register only once. 
        '''
        
        comm_reg = (0b00010 << 3) + register

        if register == self.AD7730_STATUS_REG:
            bytes_num = 1
        elif register == self.AD7730_DATA_REG:
            bytes_num = 3
        elif register == self.AD7730_MODE_REG:
            bytes_num = 2
        elif register == self.AD7730_FILTER_REG:
            bytes_num = 3
        elif register == self.AD7730_DAC_REG:
            bytes_num = 1
        elif register == self.AD7730_OFFSET_REG:
            bytes_num = 3
        elif register == self.AD7730_GAIN_REG:
            bytes_num = 3
        elif register == self.AD7730_TEST_REG:
            bytes_num = 3

        command = [comm_reg] + ([0x00] * bytes_num)
        spi.SPI_write(self.CS, command)
        data = spi.SPI_read(bytes_num + 1)        
        return data[1:]

    def getStatus(self):

        """
        RDY - Ready Bit. This bit provides the status of the RDY flag from the part. The status and function of this bit is the same as the RDY output pin. A number of events set the RDY bit high as indicated in Table XVIII in datasheet

        STDY - Steady Bit. This bit is updated when the filter writes a result to the Data Register. If the filter is
        in FASTStep mode (see Filter Register section) and responding to a step input, the STDY bit
        remains high as the initial conversion results become available. The RDY output and bit are set
        low on these initial conversions to indicate that a result is available. If the STDY is high, however,
        it indicates that the result being provided is not from a fully settled second-stage FIR filter. When the
        FIR filter has fully settled, the STDY bit will go low coincident with RDY. If the part is never placed
        into its FASTStep mode, the STDY bit will go low at the first Data Register read and it is
        not cleared by subsequent Data Register reads. A number of events set the STDY bit high as indicated in Table XVIII. STDY is set high along with RDY by all events in the table except a Data Register read.

        STBY - Standby Bit. This bit indicates whether the AD7730 is in its Standby Mode or normal mode of
        operation. The part can be placed in its standby mode using the STANDBY input pin or by
        writing 011 to the MD2 to MD0 bits of the Mode Register. The power-on/reset status of this bit
        is 0 assuming the STANDBY pin is high.





NOREF - No Reference Bit. If the voltage between the REF IN(+) and REF IN(-) pins is below 0.3 V, or either of these inputs is open-circuit, the NOREF bit goes to 1. If NOREF is active on completion of a conversion, the Data Register is loaded with all 1s. If NOREF is active on completion of a calibration, updating of the calibration registers is inhibited."""

        status = self.single_read(self.AD7730_STATUS_REG)
        bits_values = dict([('NOREF',status[0] & 0x10 == 0x10),
                            ('STBY',status[0] & 0x20 == 0x20),
                            ('STDY',status[0] & 0x40 == 0x40),
                            ('RDY',status[0] & 0x80 == 0x80)])
        return bits_values

    def getData(self):
        data = self.single_read(self.AD7730_DATA_REG)
        value = (data[0] << 15) + (data[1] << 7) + data[2]
        return value

    def IsBusy(self):
        """ Return True if ADC is busy """
        status = self.getStatus()
        return status['RDY']


    def setMode(self
                    ,mode  
                    ,polarity 
                    ,den 
                    ,iovalue 
                    ,data_length 
                    ,reference 
                    ,input_range 
                    ,clock_enable 
                    ,burn_out 
                    ,channel):
        '''
        def setMode(self
                    ,mode = self.AD7730_IDLE_MODE 
                    ,polarity = self.AD7730_UNIPOLAR_MODE
                    ,den = self.AD7730_IODISABLE_MODE
                    ,iovalue = 0b00
                    ,data_lenght = self.AD7730_24bitDATA_MODE
                    ,reference = self.AD7730_REFERENCE_5V
                    ,input_range = self.AD7730_40mVIR_MODE
                    ,clock_enable = self.AD7730_MCLK_ENABLE_MODE
                    ,burn_out = self.AD7730_BURNOUT_DISABLE
                    ,channel = self.AD7730_AIN1P_AIN1N
               ):
        '''
        mode_MSB = (mode << 5) + (polarity << 4) + (den << 3) + (iovalue << 1) + data_length
        mode_LSB = (reference << 7) + (0b0 << 6) + (input_range << 4) + (clock_enable << 3) + (burn_out << 2) + channel
    
        self.single_write(self.AD7730_MODE_REG, [mode_MSB, mode_LSB])

    def setFilter(self):
        data = self.single_read(self.AD7730_FILTER_REG)
        data[2] = data[2] | 0b00110011
        self.single_write(self.AD7730_FILTER_REG, data)
        return data

"""canvas = scene.SceneCanvas(keys='interactive', show=True, size=(1024, 768))
grid = canvas.central_widget.add_grid()
view = grid.add_view(0, 1)
view.camera = scene.MagnifyCamera(mag=1, size_factor=0.5, radius_ratio=0.6)

# Add axes
yax = scene.AxisWidget(orientation='left')
yax.stretch = (0.05, 1)
grid.add_widget(yax, 0, 0)
yax.link_view(view)

xax = scene.AxisWidget(orientation='bottom')
xax.stretch = (1, 0.05)
grid.add_widget(xax, 1, 1)
xax.link_view(view)


N = 4
M = 1000

view.camera.rect = (0, 526200, 1, 500)

lines = scene.ScrollingLines(n_lines=N, line_size=M, columns=1, dx=0.8/M, #color = 'red',
                             cell_size=(1, 8), parent=view.scene)
lines.transform = scene.STTransform(scale=(1, 1/8.))

"""

cfg = config.Config(
    i2c = {
        "port": 8,
    },

    bus = [
        { "name":"spi", "type":"i2cspi", "address": 0x28},
    ],
)

cfg.initialize()

print "SPI weight scale sensor with SPI interface. The interface is connected to the I2CSPI module which translates signalls. \r\n"

spi = cfg.get_device("spi")

try:
    print "SPI configuration.."
    spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_LOW_DATA_EDGE_LEADING| spi.I2CSPI_CLK_461kHz)
    spi.GPIO_config(spi.I2CSPI_SS2 | spi.I2CSPI_SS3, spi.SS2_INPUT | spi.SS3_INPUT)

    print "Weight scale configuration.."
    scale = BRIDGEADC01(spi.I2CSPI_SS0)
    scale.reset()


    scale.setMode(
                     mode = scale.AD7730_INT_FULL_CALIBRATION
                    ,polarity = scale.AD7730_UNIPOLAR_MODE
                    ,den = scale.AD7730_IODISABLE_MODE
                    ,iovalue = 0b00
                    ,data_length = scale.AD7730_24bitDATA_MODE
                    ,reference = scale.AD7730_REFERENCE_5V
                    ,input_range = scale.AD7730_80mVIR_MODE
                    ,clock_enable = scale.AD7730_MCLK_ENABLE_MODE
                    ,burn_out = scale.AD7730_BURNOUT_DISABLE
                    ,channel = scale.AD7730_AIN1P_AIN1N
				)
    print "Internal Full scale calibration started"

    while scale.IsBusy():            ## wait for RDY pin to go low to indicate end of callibration cycle. 
        print scale.single_read(scale.AD7730_MODE_REG)
        time.sleep(0.1)

    print "Full scale calibration completed. Start zero scale calibration"



#    spi.SPI_write(spi.I2CSPI_SS0, [0x02, 0x91, 0x80])
    scale.setMode(
                     mode = scale.AD7730_INT_ZERO_CALIBRATION
                    ,polarity = scale.AD7730_UNIPOLAR_MODE
                    ,den = scale.AD7730_IODISABLE_MODE
                    ,iovalue = 0b00
                    ,data_length = scale.AD7730_24bitDATA_MODE
                    ,reference = scale.AD7730_REFERENCE_5V
                    ,input_range = scale.AD7730_80mVIR_MODE
                    ,clock_enable = scale.AD7730_MCLK_ENABLE_MODE
                    ,burn_out = scale.AD7730_BURNOUT_DISABLE
                    ,channel = scale.AD7730_AIN1P_AIN1N
                )

    while scale.IsBusy():            ## wait for RDY pin to go low to indicate end of callibration cycle. 
        print scale.getStatus()
        time.sleep(0.1)

    print "Zero scale calibration completed.. Start reading the data.."

    scale.setMode(
                 mode = scale.AD7730_SCONVERSION_MODE
                ,polarity = scale.AD7730_UNIPOLAR_MODE
                ,den = scale.AD7730_IODISABLE_MODE
                ,iovalue = 0b00
                ,data_length = scale.AD7730_24bitDATA_MODE
                ,reference = scale.AD7730_REFERENCE_5V
                ,input_range = scale.AD7730_80mVIR_MODE
                ,clock_enable = scale.AD7730_MCLK_ENABLE_MODE
                ,burn_out = scale.AD7730_BURNOUT_DISABLE
                ,channel = scale.AD7730_AIN1P_AIN1N
            )

    while scale.IsBusy():            ## wait for RDY pin to go low to indicate end of callibration cycle. 
        time.sleep(0.05)

    channel1 = scale.getData()

    scale.setMode(
                 mode = scale.AD7730_SCONVERSION_MODE
                ,polarity = scale.AD7730_UNIPOLAR_MODE
                ,den = scale.AD7730_IODISABLE_MODE
                ,iovalue = 0b00
                ,data_length = scale.AD7730_24bitDATA_MODE
                ,reference = scale.AD7730_REFERENCE_5V
                ,input_range = scale.AD7730_80mVIR_MODE
                ,clock_enable = scale.AD7730_MCLK_ENABLE_MODE
                ,burn_out = scale.AD7730_BURNOUT_DISABLE
                ,channel = scale.AD7730_AIN2P_AIN2N
            )

    while scale.IsBusy():            ## wait for RDY pin to go low to indicate end of callibration cycle. 
        time.sleep(0.05)

    channel2 = scale.getData()

    data = np.array([channel1, channel2])
    print data

except KeyboardInterrupt:
    sys.exit(0)

