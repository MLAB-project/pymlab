#!/usr/bin/python

#import smbus
import time
from time import sleep
import sys
import struct
from pymlab.sensors import Device
from smbus2 import i2c_msg

class SPS30(Device):
    'Python library for Sensirion SPS30 i2c airborne particles (PM0.5 - PM10) sensor.'

    def __init__(self, parent = None, address = 0x61, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.REG_START_MEASUREMENT = [0x00, 0x10]
        self.REG_STOP_MEASUREMENT = [0x01, 0x04]
        self.REG_READ_DATA_READY_FLAG = [0x02, 0x02]
        self.REG_READ_MEASURED_VALUES = [0x03, 0x00]
        self.REG_AUTO_CLEANING_INTERVAL = 0x8004
        self.REG_START_FAN_CLEAN = 0x5607
        self.REG_READ_ARTICLE_CODE = 0xD025
        self.REG_READ_SERIAL_NUMBER = 0xD033
        self.REG_RESET = [0xD3, 0x04]

    def calc_checksum(self, data):
        crc = 0xff
        for d in data:
            crc ^= d
            for bit in range(8, 0, -1):
                if bool(crc & 0x80):
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1

        return (crc & 0xff)

    def send_command(self, command, data):
        send_data = command
        for i in range(int(len(data)/2)):
           send_data += data[2*i:2*i+2] + [self.calc_checksum(data[2*i:2*i+2])]
        write = i2c_msg.write(self.address, send_data)
        self.bus.driver.smbus.i2c_rdwr(write)

    def read_command(self, command, length, raw = False):
        length = int(length/2*3)

        write = i2c_msg.write(self.address, command)
        self.bus.driver.smbus.i2c_rdwr(write)

        read = i2c_msg.read(self.address, length)
        self.bus.driver.smbus.i2c_rdwr(read)

        if raw:
            data = [read.buf[i] for i in range(read.len)]
        else:
            data = [int.from_bytes(read.buf[i], "big") for i in range(read.len)]
            #TODO: checksum validation
            del data[3-1::3] # remove every 3-rd element, checksum
        return data

    def data_ready(self):
        data = self.read_command(self.REG_READ_DATA_READY_FLAG, 2)
        return (data[1] == 1)

    def reset(self):
        print(self.bus.driver)
        write = i2c_msg.write(self.address, self.REG_RESET)
        self.bus.driver.smbus.i2c_rdwr(write)
        sleep(0.5)
        self.setup()

    def start_measurement(self):
        self.send_command(self.REG_START_MEASUREMENT, [0x03, 0x00])

    def setup(self):
        self.start_measurement()

    def get_status(self):
        pass

    def extract(self, range):
        return struct.unpack(">f", struct.pack(">L", (range[3] | range[2] << 8 | range[1] << 16 | range[0] << 24)))[0]


    def get_data(self, wait = True):
        while not self.data_ready():
            time.sleep(0.1)

        raw = self.read_command(self.REG_READ_MEASURED_VALUES, 40)
        data = {}
        data['mass_pm1'] = self.extract(raw[0:4])
        data['mass_pm2-5'] = self.extract(raw[4:8])
        data['mass_pm4'] = self.extract(raw[8:12])
        data['mass_pm10'] = self.extract(raw[12:16])

        data['number_pm0-5'] = self.extract(raw[16:20])
        data['number_pm1'] = self.extract(raw[20:24])
        data['number_pm2-5'] = self.extract(raw[24:28])
        data['number_pm4'] = self.extract(raw[28:32])
        data['number_pm10'] = self.extract(raw[32:36])

        data['tps'] = self.extract(raw[36:40])

        return data

    def clean(self):
        pass


class SEN5x(Device):
    'Python library for Sensirion SPS30 i2c airborne particles (PM0.5 - PM10) sensor.'

    def __init__(self, parent = None, address = 0x61, **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        self.REG_START_MEASUREMENT = [0x00, 0x21]
        self.REG_STOP_MEASUREMENT = [0x01, 0x04]
        self.REG_READ_DATA_READY_FLAG = [0x02, 0x02]
        self.REG_READ_MEASURED_VALUES = [0x03, 0xC4]
        self.REG_AUTO_CLEANING_INTERVAL = [0x80, 0x04]
        self.REG_START_FAN_CLEAN = [0x56, 0x07]
        self.REG_READ_ARTICLE_CODE = 0xD025
        self.REG_READ_SERIAL_NUMBER = 0xD033
        self.REG_RESET = [0xD3, 0x04]

    def calc_checksum(self, data):
        crc = 0xff
        for d in data:
            crc ^= d
            for bit in range(8, 0, -1):
                if bool(crc & 0x80):
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1

        return (crc & 0xff)

    def send_command(self, command, data):
        send_data = command
        for i in range(int(len(data)/2)):
           send_data += data[2*i:2*i+2] + [self.calc_checksum(data[2*i:2*i+2])]
        write = i2c_msg.write(self.address, send_data)
        self.bus.driver.smbus.i2c_rdwr(write)

    def read_command(self, command, length, raw = False):
        length = int(length/2*3)

        write = i2c_msg.write(self.address, command)
        self.bus.driver.smbus.i2c_rdwr(write)

        time.sleep(0.1)

        read = i2c_msg.read(self.address, length)
        self.bus.driver.smbus.i2c_rdwr(read)

        if raw:
            data = [read.buf[i] for i in range(read.len)]
        else:
            data = [int.from_bytes(read.buf[i], "big") for i in range(read.len)]
            #TODO: checksum validation
            del data[3-1::3] # remove every 3-rd element, checksum
        return data

    def data_ready(self):
        data = self.read_command(self.REG_READ_DATA_READY_FLAG, 2)
        return (data[1] == 1)

    def reset(self):
        print(self.bus.driver)
        write = i2c_msg.write(self.address, self.REG_RESET)
        self.bus.driver.smbus.i2c_rdwr(write)
        sleep(0.5)
        self.setup()

    def start_measurement(self):
        self.send_command(self.REG_START_MEASUREMENT, [])

    def setup(self):
        self.start_measurement()

    def get_status(self):
        pass

    def extract(self, range):
        return struct.unpack(">f", struct.pack(">L", (range[3] | range[2] << 8 | range[1] << 16 | range[0] << 24)))[0]


    def get_data(self, wait = True):
        while not self.data_ready():
            time.sleep(0.1)

        raw = self.read_command(self.REG_READ_MEASURED_VALUES, 40)
        data = {}
        data['mass_pm1'] = (raw[1] | raw[0]<<8) /  10.0
        data['mass_pm2-5'] = (raw[3] | raw[2]<<8) /  10.0
        data['mass_pm4'] = (raw[5] | raw[4]<<8) /  10.0
        data['mass_pm10'] = (raw[7] | raw[6]<<8) /  10.0

        data['hum'] = (raw[9] | raw[8]<<8) /  100.0
        data['temp'] = (raw[11] | raw[10]<<8) /  200.0
        data['voc'] = (raw[13] | raw[12]<<8) /  11.0
        data['nox'] = (raw[15] | raw[14]<<8) /  10.0

        return data

    def clean(self):
        pass
