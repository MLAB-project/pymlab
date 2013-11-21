#!/usr/bin/env python

import logging

import smbus

from pymlab.sensors import Device, SimpleBus

    
#MPL3115A register address
MPL3115_STATUS              =0x00
MPL3115_PRESSURE_DATA       =0x01
MPL3115_DR_STATUS           =0x06
MPL3115_DELTA_DATA          =0x07
MPL3115_WHO_AM_I            =0x0c
MPL3115_FIFO_STATUS         =0x0d
MPL3115_FIFO_DATA           =0x0e
MPL3115_FIFO_SETUP          =0x0e
MPL3115_TIME_DELAY          =0x10
MPL3115_SYS_MODE            =0x11
MPL3115_INT_SORCE           =0x12
MPL3115_PT_DATA_CFG         =0x13
MPL3115_BAR_IN_MSB          =0x14
MPL3115_P_ARLARM_MSB        =0x16
MPL3115_T_ARLARM            =0x18
MPL3115_P_ARLARM_WND_MSB    =0x19
MPL3115_T_ARLARM_WND        =0x1b
MPL3115_P_MIN_DATA          =0x1c
MPL3115_T_MIN_DATA          =0x1f
MPL3115_P_MAX_DATA          =0x21
MPL3115_T_MAX_DATA          =0x24
MPL3115_CTRL_REG1           =0x26
MPL3115_CTRL_REG2           =0x27
MPL3115_CTRL_REG3           =0x28
MPL3115_CTRL_REG4           =0x29
MPL3115_CTRL_REG5           =0x2a
MPL3115_OFFSET_P            =0x2b
MPL3115_OFFSET_T            =0x2c
MPL3115_OFFSET_H            =0x2d


def altimet(Device):

    # Set to Altimeter with an OSR = 128 
    device.writeI2C(MPL3115_CTRL_REG1, "0xB8")
    # Enable Data Flags in PT_DATA_CFG
    device.writeI2C(MPL3115_PT_DATA_CFG, "0x07")
    # Set Active (polling)
    device.writeI2C(MPL3115_CTRL_REG1, "0xB9")

    while not rospy.is_shutdown():
        # Read STATUS Register
        STA = device.readI2C(MPL3115_STATUS)
        # check if pressure or temperature are ready (both) [STATUS, 0x00 register]
        if STA == "":
            print "error with the sensor"
            break
        if (int(STA,16) & 0x04) == 4:
            # OUT_P
            OUT_P_MSB = device.readI2C("0x01")
            OUT_P_CSB = device.readI2C("0x02")
            OUT_P_LSB = device.readI2C("0x04")
            ## OUT_T
            #OUT_T_MSB = readI2C(0x04)
            #OUT_T_LSB = readI2C(0x05)

            #print OUT_P_MSB
            #print OUT_P_CSB
            #print OUT_P_LSB
    
            #treat the bits to get the altitude
            signedvalue = OUT_P_MSB+OUT_P_CSB[2:]
            fraction = OUT_P_LSB[:3]
    
            #print int(signedvalue,16)
            #print int(fraction,16)

            str = "signedvalue: %s" % signedvalue
            rospy.loginfo(str)
            pub.publish(String(str))

        else:
            #print "data not ready"
            pass
        rospy.sleep(1.0)

if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
