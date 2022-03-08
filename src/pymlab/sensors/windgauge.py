#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time
import sys
import os

from pymlab.sensors import Device


class WINDGAUGE03A(Device):

    def __init__(self, parent = None, address = 0x68, sdp3x_address = 0x21, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.r_outer = 0.018 # outer venturi tube diameter [m]
        self.r_inner = 0.009 # inner venturi tube diameter [m]
        self.air_density = 1.029 # density of air [kg/m^3]
        self.mag_declination = 4.232 # magnetic declination in deg from true north

        self.sdp3x_i2c_address = sdp3x_address
        self.mag_i2c_address = 0x0C

        ## USER BANK 0 REGISTERS
        self.ICM20948_WHO_AM_I = 0x00
        self.ICM20948_USER_CTRL = 0x03
        self.ICM20948_LP_CONFIG = 0x05
        self.ICM20948_PWR_MGMT_1 = 0x06
        self.ICM20948_PWR_MGMT_2 = 0x07
        self.ICM20948_INT_PIN_CFG = 0x0F
        self.ICM20948_INT_ENABLE = 0x10
        self.ICM20948_I2C_MST_STATUS = 0x17
        self.ICM20948_ACEL_XOUT_H = 0x2D
        self.ICM20948_ACEL_XOUT_L = 0x2E
        self.ICM20948_ACEL_YOUT_H = 0x2F
        self.ICM20948_ACEL_YOUT_L = 0x30
        self.ICM20948_ACEL_ZOUT_H = 0x31
        self.ICM20948_ACEL_XOUT_L = 0x32
        self.ICM20948_GYRO_XOUT_H = 0x33
        self.ICM20948_GYRO_XOUT_L = 0x34
        self.ICM20948_GYRO_YOUT_H = 0x35
        self.ICM20948_GYRO_YOUT_L = 0x36
        self.ICM20948_GYRO_ZOUT_H = 0x37
        self.ICM20948_GYRO_XOUT_L = 0x38
        self.ICM20948_TEMP_OUT_H = 0x39
        self.ICM20948_TEMP_OUT_L = 0x3A
        self.ICM20948_EXT_SLV_SENS_DATA_00 = 0x3B
        # self.ICM20948_EXT_SLV_SENS_DATA_01 = 0x3C

        # USER BANK 2 REGISTERS
        self.ICM20948_GYRO_CONFIG = 0x01
        self.ICM20948_ODR_ALIGN_EN = 0x09
        self.ICM20948_ACCEL_SMPLRT_DIV_1 = 0x10
        self.ICM20948_ACCEL_SMPLRT_DIV_2 = 0x11
        self.ICM20948_ACEL_CONFIG = 0x14
        self.ICM20948_ACEL_CONFIG_2 = 0x15


        ## USER BANK 3 REGISTERS
        self.ICM20948_I2C_SLV0_ADDR = 0x03
        self.ICM20948_I2C_SLV0_REG = 0x04 # I2C slave 0 register address from where to begin data transfer.
        self.ICM20948_I2C_SLV0_CTRL  = 0x05
        self.ICM20948_I2C_SLV0_DO = 0x06

        self.ICM20948_I2C_SLV1_ADDR = 0x07
        self.ICM20948_I2C_SLV1_REG = 0x08 # I2C slave 1 register address from where to begin data transfer.
        self.ICM20948_I2C_SLV1_CTRL  = 0x09
        self.ICM20948_I2C_SLV1_DO = 0x0A

        ## USER BANK REGISTERS 0-3
        self.ICM20948_REG_BANK_SEL = 0x7F # 0

        ## MAGNETOMETER REGISTERS
        self.AK09916_WIA2 = 0x01 # WHO_AM_I[7:0] = 0x09
        self.AK09916_ST1 = 0x10 # STATUS_1[1] = DOR (data overrun); STATUS_1[0] = DRDY (data ready)
        self.AK09916_HXL = 0x11 # HXL[7:0] = X-axis measurement data lower 8bit
        self.AK09916_HXH = 0x12 # HXH[15:8] = X-axis measurement data higher 8bit
        self.AK09916_HYL = 0x13 # HYL[7:0] = Y-axis measurement data lower 8bit
        self.AK09916_HYH = 0x14 # HYH[15:8] = Y-axis measurement data higher 8bit
        self.AK09916_HZL = 0x15 # HZL[7:0] = Z-axis measurement data lower 8bit
        self.AK09916_HZH = 0x16 # HZH[15:8] = Z-axis measurement data higher 8bit
        self.AK09916_ST2 = 0x18 # STATUS_2[3] = HOFL (magnetic sensor overflow)
        self.AK09916_CNTL2 = 0x31 # CONTROL_2[4:0] =
        """
                                                        “00000”: Power-down mode
                                                        “00001”: Single measurement mode
                                                        “00010”: Continuous measurement mode 1 (10Hz)
                                                        “00100”: Continuous measurement mode 2 (20Hz)
                                                        “00110”: Continuous measurement mode 3 (50Hz)
                                                        “01000”: Continuous measurement mode 4 (100Hz)
                                                        “10000”: Self-test mode
        """
        self.AK09916_CNTL3 = 0x32 # CONTROL_3[0] = SRST (soft reset)



        self.TRIGGER_MEASUREMENT = [0x36, 0x1E]           # SDP3x command: trigger continuos differential pressure measurement
        self.TRIGGER_MEASUREMENT_2 = [0x36, 0x15]         # SDP3x command: trigger differential pressure measurement with averaging until read
        self.SOFT_RESET          = 0x06                   # SDP3x command: soft reset
        self.READ_PRODUCT_IDENTIFIER1 = [0x36, 0x7c]      # SDP3x command: read product idetifier register
        self.READ_PRODUCT_IDENTIFIER2 = [0xE1, 0x02]
        self.SDP3x_tsf = 200.0 #temperature scaling factor (same for all SDP3X sensors)


    def usr_bank_sel(self, usr_bank_reg):
        self.bus.write_byte_data(self.address, self.ICM20948_REG_BANK_SEL, usr_bank_reg << 4)

    def write_icm20948_reg_data(self, reg_address, reg_usr_bank, value):
        self.usr_bank_sel(reg_usr_bank)
        self.bus.write_byte_data(self.address, reg_address, value)

    def read_icm20948_reg_data(self, reg_address, reg_usr_bank, num_of_bytes):
        self.usr_bank_sel(reg_usr_bank)
        if num_of_bytes > 1:
            return(self.bus.read_i2c_block_data(self.address, reg_address, num_of_bytes))
        else:
            return((self.bus.read_byte_data(self.address, reg_address)))

    def reset (self):
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x01 | 1 << 7) # ICM20948 - reset device and register values
        time.sleep(0.1)
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x01) # PWR_MGMT_1[6] (SLEEP) set to 0 - !!!DEVICE WAKEUP!!!; PWR_MGMT_1[2:0] (CLKSEL) = "001" for optimal performance
        self.write_icm20948_reg_data(self.ICM20948_INT_PIN_CFG, 0, 0x02) # INT_PIN_CFG[1] (BYPASS_ENABLE) = 1 !ENABLE BYPASS OF ICM20948's I2C INTERFACE! (SDA and SCL connected directly to auxilary AUX_DA and AUX_CL)
        self.bus.write_byte(self.sdp3x_i2c_address, 0x00) # SDP3x device wakeup
        time.sleep(0.1)
        self.bus.write_byte(0x00, 0x06) # SDP3x device soft reset
        time.sleep(0.1)

    def initialize (self):

        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x01) # PWR_MGMT_1[6] (SLEEP) set to 0 - !!!DEVICE WAKEUP!!!; PWR_MGMT_1[2:0] (CLKSEL) = "001" for optimal performance
        # time.sleep(0.1)

        ### ICM20948 accelerometer configuration
        # self.write_icm20948_reg_data(self.ICM20948_ODR_ALIGN_EN, 2, 0x01)
        # # self.write_icm20948_reg_data(self.ICM20948_ACCEL_SMPLRT_DIV_2, 2, 0x04)
        # # self.write_icm20948_reg_data(self.ICM20948_ACCEL_SMPLRT_DIV_2, 2, 0x65) # LSB for accel sample div. rate ( ODR = 1.125 kHz/(1+ACCEL_SMPLRT_DIV[11:0])) - set to 10 Hz
        # self.write_icm20948_reg_data(self.ICM20948_ACCEL_SMPLRT_DIV_2, 2, 0x0F)
        # self.write_icm20948_reg_data(self.ICM20948_ACCEL_SMPLRT_DIV_2, 2, 0xFF) # LSB for accel sample div. rate ( ODR = 1.125 kHz/(1+ACCEL_SMPLRT_DIV[11:0])) - set to 10 Hz

        # self.write_icm20948_reg_data(self.ICM20948_ACCEL_SMPLRT_DIV_2, 2, 0x70) # LSB for accel sample div. rate ( ODR = 1.125 kHz/(1+ACCEL_SMPLRT_DIV[11:0])) - set to 10 Hz
        # self.write_icm20948_reg_data(self.ICM20948_ACEL_CONFIG, 2, 0x09) # enable accel DPLF and set it to 23.9 Hz
        # self.write_icm20948_reg_data(self.ICM20948_ACEL_CONFIG_2, 2, 0x03) #

        ### SDP3X sensor configuration #####################
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00)   # USER_CTRL[5] (I2C_MST_EN) = 0
        self.write_icm20948_reg_data(self.ICM20948_INT_PIN_CFG, 0, 0x02) # INT_PIN_CFG[1] (BYPASS_ENABLE) = 1 !ENABLE BYPASS OF ICM20948's I2C INTERFACE! (SDA and SCL connected directly to auxilary AUX_DA and AUX_CL)
        self.bus.write_byte(self.sdp3x_i2c_address, 0x00) # SDP3x device wakeup
        time.sleep(0.1)
        self.bus.write_byte_data(self.sdp3x_i2c_address, 0x36, 0x7C)
        self.bus.write_byte_data(self.sdp3x_i2c_address, 0xE1, 0x02)
        p_id = self.bus.read_i2c_block(self.sdp3x_i2c_address, 18)
        p_num = ((p_id[0] << 24) | (p_id[1] << 16) | (p_id[3] << 8) | p_id[4])

        if (p_num == 0x03010101):
            sensor = "SDP31 500Pa"
        elif (p_num == 0x03010201):
            sensor = "SDP32 125Pa"
        elif (p_num == 0x03010384):
            sensor = "SDP33 1500Pa"
        else:
            sensor = "unknown"
        print("ID: %s - sensor: %s" % (hex(p_num), sensor))

        if (os.path.isfile("ICM20948_mag_cal.txt")):
            print("Magnetometer calibrated.\n")
        else:
            print("Magnetometer not calibrated.\n")

        self.bus.write_byte_data(self.sdp3x_i2c_address, self.TRIGGER_MEASUREMENT[0], self.TRIGGER_MEASUREMENT[1] )  # send "trigger continuos measurement" command to SDP3X sensor to begin diff. pressure and temperature measurement
        time.sleep(0.1)
        self.i2c_master_read(0, self.sdp3x_i2c_address, 9, 0x00) # configure SDP3X as slave_0 of IMU's I2C master

        ### ICM-20948 magnetometer configuration #####################
        self.i2c_master_write(1, self.mag_i2c_address, 0x08, self.AK09916_CNTL2) # configure magnetometer to begin magnetic flux measurement with frequency of 100 Hz (for measurement frequency options ref. to AK09916_CNTL2)
        self.i2c_master_read(1, self.mag_i2c_address, 9, 0x10)

    def stop(self):
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00)   # USER_CTRL[5] (I2C_MST_EN) = 0
        self.write_icm20948_reg_data(self.ICM20948_INT_PIN_CFG, 0, 0x02) # INT_PIN_CFG[1] (BYPASS_ENABLE) = 1 !ENABLE BYPASS OF ICM20948's I2C INTERFACE! (SDA and SCL connected directly to auxilary AUX_DA and AUX_CL)
        self.bus.write_byte_data(self.sdp3x_i2c_address, 0x3F, 0xF9) # SDP3x stop continuous measurement command
        self.bus.write_byte_data(self.sdp3x_i2c_address, 0x36, 0x77) # SDP3x enter sleep mode
        self.write_icm20948_reg_data(self.ICM20948_PWR_MGMT_1, 0, 0x21) # PWR_MGMT_1[6] (SLEEP) set to 1 - !!!DEVICE PUT IN SLEEP MODE!!!; PWR_MGMT_1[2:0] (CLKSEL) = "001" for optimal performance

    def i2c_master_write (self, slv_id, slv_addr, data_out, slv_reg ): #
        slv_reg_shift = 4 * slv_id
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20)                         # USER_CTRL[5] (I2C_MST_EN) = 1
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_DO + slv_reg_shift, 3, data_out)     # I2C_SLVX_DO[7:0] = data_out
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR + slv_reg_shift, 3, slv_addr)   # I2C_SLVX_ADDR[6:0] = (slv_addr | I2C_SLV0_RNW) - slave addres | R/W bit MSB (W: 0)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG + slv_reg_shift, 3, slv_reg)     # I2C_SLVX_REG[7:0] = slv_reg
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + slv_reg_shift, 3, 0x8a)       # I2C_SLVX_CTRL[7] (I2C_SLVX_EN) = 1, I2C_SLVX_CTRL[5] (I2C_SLVX_REG_DIS) = 0
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + slv_reg_shift, 3, 0x00)       # I2C_SLVX_CTRL[7] (I2C_SLVX_EN) = 0
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x00)                         # USER_CTRL[5] (I2C_MST_EN) = 0

    def i2c_master_read (self, slv_id, slv_addr, slv_rd_len, slv_reg ): #
        slv_reg_shift = 4 * slv_id
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_ADDR + slv_reg_shift, 3, slv_addr | (1 << 7))   # I2C_SLVX_ADDR[6:0] = (slv_addr | I2C_SLV0_RNW) - slave addres | R/W bit MSB (R: 1)
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_REG + slv_reg_shift, 3, slv_reg)                # I2C_SLVX_REG[7:0] = slv_reg
        self.write_icm20948_reg_data(self.ICM20948_I2C_SLV0_CTRL + slv_reg_shift, 3, 0x80 | slv_rd_len)     # I2C_SLVX_CTRL[7] (I2C_SLVX_EN) = 1, I2C_SLVX_LENG[3:0] = slv_rd_len (number of bytes to be read from slave (0-15))
        self.write_icm20948_reg_data(self.ICM20948_USER_CTRL, 0, 0x20)                                      # USER_CTRL[5] (I2C_MST_EN) = 1

    def get_temp(self):
        room_temp_offset = 21.0
        temp_sens = 333.87
        temp_raw_data = self.read_icm20948_reg_data(self.ICM20948_TEMP_OUT_H, 0, 2)
        temp_raw = ((temp_raw_data[0] << 8) + temp_raw_data[1])
        return(((temp_raw - room_temp_offset)/temp_sens) + room_temp_offset)

    def get_accel(self):
        accel_sens = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_ACEL_CONFIG, 2, 1) & 0x6))) * 2048)
        accel_raw = self.read_icm20948_reg_data(self.ICM20948_ACEL_XOUT_H, 0, 6)
        accel_x_raw = ((accel_raw[0] << 8) + accel_raw[1])
        accel_y_raw = ((accel_raw[2] << 8) + accel_raw[3])
        accel_z_raw = ((accel_raw[4] << 8) + accel_raw[5])

        if accel_x_raw > 0x7fff:
            accel_x_raw -= 65536
        if accel_y_raw > 0x7fff:
            accel_y_raw -= 65536
        if accel_z_raw > 0x7fff:
            accel_z_raw -= 65536

        return((accel_x_raw / accel_sens), (accel_y_raw / accel_sens), (accel_z_raw / accel_sens) )

    def get_gyro(self):
        gyro_sens = float((1 << (3 - (self.read_icm20948_reg_data(self.ICM20948_GYRO_CONFIG, 2, 1) & 0x6))) * 16.4)
        gyro_raw = self.read_icm20948_reg_data(self.ICM20948_GYRO_XOUT_H, 0, 6)
        gyro_x_raw = ((gyro_raw[0] << 8) + gyro_raw[1])
        gyro_y_raw = ((gyro_raw[2] << 8) + gyro_raw[3])
        gyro_z_raw = ((gyro_raw[4] << 8) + gyro_raw[5])

        if gyro_x_raw > 0x7fff:
            gyro_x_raw -= 65536
        if gyro_y_raw > 0x7fff:
            gyro_y_raw -= 65536
        if gyro_z_raw > 0x7fff:
            gyro_z_raw -= 65536

        return((gyro_x_raw / gyro_sens), (gyro_y_raw / gyro_sens), (gyro_z_raw / gyro_sens))

    def get_mag_raw(self, *args):

        mag_raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00 + 9, 0, 9)

        magX = (mag_raw_data[2] << 8) + mag_raw_data[1]
        magY = (mag_raw_data[4] << 8) + mag_raw_data[3]
        magZ = (mag_raw_data[6] << 8) + mag_raw_data[5]

        if magX > 0x7fff:
            magX -= 65536
        if magY > 0x7fff:
            magY -= 65536
        if magZ > 0x7fff:
            magZ -= 65536

        mag_scf = 4912/32752.0

        return(magX, magY, magZ)


    def get_mag(self, *args):

        offset_x, offset_y, offset_z = 0, 0, 0
        scale_x, scale_y, scale_z = 1, 1, 1

        if (not args) & (os.path.isfile("ICM20948_mag_cal.txt")):
            cal_file = open("ICM20948_mag_cal.txt", "r")

            cal_consts = cal_file.readline().split(",")

            offset_x = float(cal_consts[0])
            offset_y = float(cal_consts[1])
            offset_z = float(cal_consts[2])

            scale_x = float(cal_consts[3])
            scale_y = float(cal_consts[4])
            scale_z = float(cal_consts[5])

        mag_raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00 + 9, 0, 9)

        magX = (mag_raw_data[2] << 8) + mag_raw_data[1]
        magY = (mag_raw_data[4] << 8) + mag_raw_data[3]
        magZ = (mag_raw_data[6] << 8) + mag_raw_data[5]

        if magX > 0x7fff:
            magX -= 65536
        if magY > 0x7fff:
            magY -= 65536
        if magZ > 0x7fff:
            magZ -= 65536

        mag_scf = 4912/32752.0

        return(((magX*mag_scf) - offset_x) * scale_x, ((magY*mag_scf) - offset_y) * scale_y, ((magZ*mag_scf) - offset_z)*scale_z)

    def calib_mag(self, calib_time):
        try:
            decision = False
            print("\nDo you wish to perform new magnetometer calibration? Old calibration data will be lost!")


            while not decision:
                start_cal =  input("[Y/N]\n")
                if (start_cal == 'N') or (start_cal == 'n'):
                    print("\nCalibration canceled, no new calibration values saved.\n\n")
                    self.stop()
                    sys.exit(1)
                elif (start_cal == 'Y') or (start_cal == 'y'):
                    decision = True

            self.initialize()
            delay = 5
            print("\nStarting calibration in %d seconds with duration of %d seconds! Please manually rotate by sensor to every direction\n" % (delay, calib_time))
            time.sleep(1)
            for i in range(delay):
                print(str(delay-i))
                time.sleep(1)

            print("Calibration has started!\n")

            t_end = time.time() + calib_time
            mag_x = []
            mag_y = []
            mag_z = []

            while time.time() < t_end:
                mag_x_i, mag_y_i, mag_z_i = self.get_mag(True)
                mag_x.append(mag_x_i)
                mag_y.append(mag_y_i)
                mag_z.append(mag_z_i)
                print("%f,%f,%f\n" % (mag_x_i, mag_y_i, mag_z_i))

            ### HARDIRON COMPAS COMPENSATION

            offset_x = (max(mag_x) + min(mag_x)) / 2
            offset_y = (max(mag_y) + min(mag_y)) / 2
            offset_z = (max(mag_z) + min(mag_z)) / 2

            ### SOFTIRON COMPASS COMPENSATION

            avg_delta_x = (max(mag_x) - min(mag_x)) / 2
            avg_delta_y = (max(mag_y) - min(mag_y)) / 2
            avg_delta_z = (max(mag_z) - min(mag_z)) / 2

            avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3

            scale_x = avg_delta / avg_delta_x
            scale_y = avg_delta / avg_delta_y
            scale_z = avg_delta / avg_delta_z

            decision = False
            print("\nFinished. Do you wish to save calibration data?")

            while not decision:
                start_cal =  input("[Y/N]\n")
                if (start_cal == 'N') or (start_cal == 'n'):
                    print("\nCalibration canceled, no new calibration values saved.\n\n")
                    self.stop()
                    sys.exit(1)
                elif (start_cal == 'Y') or (start_cal == 'y'):
                    decision = True

        except KeyboardInterrupt:

            print("\nCalibration canceled, no new calibration values saved.\n\n")
            self.stop()
            sys.exit(0)

        cal_file = open("ICM20948_mag_cal.txt", "w")
        cal_file.write("%f,%f,%f,%f,%f,%f" % (offset_x, offset_y, offset_z, scale_x, scale_y, scale_z))
        cal_file.close()

        sys.stdout.write("Calibration successful!\n\n")

    def get_dp(self):
        raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00, 0x00, 9)
        press_data = raw_data[0]<<8 | raw_data[1]

        if (press_data > 0x7fff):
            press_data -= 65536

        dpsf = float(raw_data[6]<<8 | raw_data[7]) # SDP3X sensor scaling factor obtained from byte 6 and 7 of read message
        if(dpsf == 0):
            return(0.0)
        else:
            return(press_data/dpsf)

    def get_t(self):
        raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00, 0x00, 5)
        temp_data = raw_data[3]<<8 | raw_data[4]

        return(temp_data/self.SDP3x_tsf)

    def get_t_dp(self):
        raw_data = self.read_icm20948_reg_data(self.ICM20948_EXT_SLV_SENS_DATA_00, 0x00, 9)
        press_data = raw_data[0]<<8 | raw_data[1]
        temp_data = raw_data[3]<<8 | raw_data[4]

        if (press_data > 0x7fff):
            press_data -= 65536

        if (temp_data > 0x7fff):
            temp_data -= 65536

        dpsf = float(raw_data[6]<<8 | raw_data[7]) # SDP3X sensor scaling factor obtained from byte 6 and 7 of read message

        return((press_data/dpsf), (temp_data/self.SDP3x_tsf))

    def get_dp_spd(self): # function for computation of air-flow speed from diff. pressure in venturi tube (given diff. pressure, outer diameter, inner diameter and air density)
        dp = self.get_dp()
        a_outer = math.pi*(self.r_outer**2)
        a_inner = math.pi*(self.r_inner**2)
        ratio = a_outer/a_inner
        if dp < 0:
            spd = math.sqrt(((2*-dp)/((ratio**2-1)*self.air_density)))
        elif dp == 0:
            spd = 0
        else:
            spd = -math.sqrt(((2*(dp)/((ratio**2-1)*self.air_density)))) # positive speed from negative pressure is due to backwards mounting of SDP3x sensor in venturi tube
        return(dp, spd)

    def get_mag_hdg(self):
        mag_raw = list(self.get_mag())
        accel_raw = list(self.get_accel())

        if accel_raw[2] < 0: # switch X and Z axis sign in case the sensor is turned upside down
            mag_raw[0] = - mag_raw[0]
            mag_raw[2] = - mag_raw[2]

            accel_raw[0] = - accel_raw[0]
            accel_raw[2] = - accel_raw[2]

        # Normalize accelerometer raw values.
        if(sum(accel_raw) == 0):
            acc_x_norm = 0
            acc_y_norm = 0
        else:
            acc_x_norm = accel_raw[0]/math.sqrt(accel_raw[0]**2 + accel_raw[1]**2 + accel_raw[2]**2)
            acc_y_norm = accel_raw[1]/math.sqrt(accel_raw[0]**2 + accel_raw[1]**2 + accel_raw[2]**2)

        # Calculate pitch and roll
        pitch = math.asin(acc_y_norm);

        if abs(pitch) == math.pi:
            roll = 0
        else:
            if (-acc_x_norm/math.cos(pitch)) > 1:
                roll = math.pi
            elif (-acc_x_norm/math.cos(pitch)) < -1:
                roll = -math.pi
            else:
                roll = math.asin(-acc_x_norm/math.cos(pitch))

        # Calculate the new tilt compensated values
        mag_x_comp = -mag_raw[1]*math.cos(pitch) + mag_raw[2]*math.sin(pitch);
        mag_y_comp = (mag_raw[1]*math.sin(roll)*math.sin(pitch) + mag_raw[0]*math.cos(roll) - mag_raw[2]*math.sin(roll)*math.cos(pitch))

        if mag_x_comp != 0:
            mag_hdg_comp = math.atan2(-mag_y_comp, mag_x_comp)*(180/math.pi) + self.mag_declination
        else:
            if mag_y_comp < 0:
                mag_hdg_comp = -90
            elif mag_y_comp > 0:
                mag_hdg_comp = +90
            else:
                mag_hdg_comp = 0

        if(mag_hdg_comp < 0):
            mag_hdg_comp += 360

        return(mag_hdg_comp)
