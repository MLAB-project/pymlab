#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors.iic module.

Author: Jan Milik <milikjan@fit.cvut.cz>
"""
import time
import struct

class Driver(object):
    def write_byte(self, address, value):
        raise NotImplementedError()
    
    def read_byte(self, address):
        raise NotImplementedError()
    
    def write_byte_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_byte_data(self, address, register):
        raise NotImplementedError()
    
    def write_word_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_word_data(self, address, register):
        raise NotImplementedError()
    
    def write_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_block_data(self, address, register):
        raise NotImplementedError()

    def get_driver(self):
        return self.driver_type



class SMBusDriver(Driver):

    def __init__(self, port, smbus):
        self.port = port
        self.smbus = smbus
        self.driver_type = 'smbus'
    
    def write_byte(self, address, value):
        return self.smbus.write_byte(address, value)
    
    def read_byte(self, address):
        return self.smbus.read_byte(address)
    
    def write_byte_data(self, address, register, value):
        return self.smbus.write_byte_data(address, register, value)
    
    def read_byte_data(self, address, register):
        return self.smbus.read_byte_data(address, register)

    def write_word_data(self, address, register, value):
        return self.smbus.write_word_data(address, register, value)
    
    def read_word_data(self, address, register):
        return self.smbus.read_word_data(address, register)
    
    def write_block_data(self, address, register, value):
        return self.smbus.write_block_data(address, register, value)
    
    def read_block_data(self, address, register):
        return self.smbus.read_block_data(address, register)

    def block_process_call(self, address, register, value):
        return self.smbus.block_process_call(address, register, value)

    ### I2C transactions not compatible with pure SMBus driver
    def write_i2c_block(self, address, value):
        return self.smbus.write_i2c_block(address, value)
  
    def read_i2c_block(self, address, length):
        return self.smbus.read_i2c_block(address, length)

    def write_i2c_block_data(self, address, register, value):
        return self.smbus.write_i2c_block_data(address, register, value)
    
    def read_i2c_block_data(self, address, register, length):
        return self.smbus.read_i2c_block_data(address, register, length)


class HIDDriver(Driver):
    def __init__(self, port = None):
        self.driver_type = 'hid'
        time.sleep(1)   # give a time to OS for remounting the HID device
        import hid
        self.h = hid.device()      
        self.h.open(0x10C4, 0xEA90, None) # Connect HID again after enumeration
        self.h.write([0x02, 0xFF, 0x00, 0x00, 0x00])  # Set GPIO to Open-Drain  
        for k in range(3):      # blinking LED
            self.h.write([0x04, 0x00, 0xFF])
            time.sleep(0.05)
            self.h.write([0x04, 0xFF, 0xFF])
            time.sleep(0.05)
        self.h.write([0x02, 0xFF, 0x00, 0xFF, 0x00])  # Set GPIO to RX/TX LED  
        # Set SMB Configuration (AN 495)
        self.h.write([0x06, 0x00, 0x01, 0x86, 0xA0, 0x02, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x01, 0x00, 0x0F])  

    def I2CError(self):
        self.h.write([0x01, 0x01]) # Reset Device for cancelling all transfers and reset configuration
        self.h.close()
        time.sleep(3)   # Give a time to OS for release the BUS
        raise IOError()

    def get_handler(self):
        return h
    
    # WARNING ! - CP2112 does not support I2C address 0    
    def write_byte(self, address, value):
        return self.h.write([0x14, address<<1, 0x01, value]) # Data Write Request
    
    def read_byte(self, address):
        self.h.write([0x10, address<<1, 0x00, 0x01]) # Data Read Request
        
        for k in range(10):
            self.h.write([0x15, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                self.h.write([0x12, 0x00, 0x01]) # Data Read Force
                response = self.h.read(4)
                return response[3]
        self.I2CError()
    
    def write_byte_data(self, address, register, value):
        return self.h.write([0x14, address<<1, 0x02, register, value]) # Data Write Request
    
    def read_byte_data(self, address, register):
        self.h.write([0x11, address<<1, 0x00, 0x01, 0x01, register]) # Data Write Read Request 

        for k in range(10):
            self.h.write([0x15, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            #print "status",map(hex,response)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                self.h.write([0x12, 0x00, 0x01]) # Data Read Force
                response = self.h.read(4)
                #print "data ",map(hex,response)
                return response[3]
        self.I2CError()
    
    def write_word_data(self, address, register, value):
        return self.h.write([0x14, address<<1, 0x03, register, value>>8, value & 0xFF]) # Word Write Request
    
    def read_word_data(self, address, register):
        self.h.write([0x11, address<<1, 0x00, 0x02, 0x01, register]) # Data Write Read Request
        self.h.write([0x12, 0x00, 0x02]) # Data Read Force
        
        for k in range(10):             # Polling a data
            response = self.h.read(10)
            #print map(hex,response)
            #print "status ",response
            if (response[0] == 0x13) and (response[2] == 2):
                return (response[4]<<8)+response[3]           
            #self.h.write([0x15, 0x01]) # Transfer Status Request
            self.h.write([0x11, address<<1, 0x00, 0x02, 0x01, register]) # Data Write Read Request
            self.h.write([0x12, 0x00, 0x02]) # Data Read Force            
        self.I2CError()
    
    def write_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_block_data(self, address, register):
        raise NotImplementedError()

    def write_i2c_block(self, address, value):
        if (len(value) > 61):
            raise IndexError()
        data = [0x14, address<<1, len(value)]  # Data Write Request (max. 61 bytes, hidapi allows max 8bytes transaction lenght)
        data.extend(value)
        return self.h.write(data) # Word Write Request
        self.I2CError()
  
    def read_i2c_block(self, address, length):
        self.h.write([0x10, address<<1, 0x00, length]) # Data Read Request (60 bytes)

        for k in range(10):
            self.h.write([0x15, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            #print "response ",map(hex,response)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                #length = (response[5]<<8)+response[6]
                self.h.write([0x12, response[5], response[6]]) # Data Read Force
                data = self.h.read(length+3)
                #print "length ",length
                #print "data ",map(hex,data)
                return data[3:]
        self.I2CError()

    def write_i2c_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_i2c_block_data(self, address, register, length = 1):
        raise NotImplementedError()



class SerialDriver(Driver): # Driver for I2C23201A modul with SC18IM700 master I2C-bus controller with UART interface
    def __init__(self, port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1.5):
        self.driver_type = 'serial'
        import serial
        self.ser = serial.Serial(port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
        self.ser.flushInput()
        self.ser.write('IP')
        if (self.ser.read() == ''):
            raise RuntimeError()
    
    def I2CError(self):
        raise NotImplementedError()

    def get_handler(self):
        raise NotImplementedError()

    def write_byte(self, address, value):
        data = 'S' + "".join(map(chr, [((address << 1) & 0xfe ), 1, value ])) + 'P'
        w = self.ser.write(data)

    def read_byte(self, address):
        data = 'S' + "".join(map(chr, [((address << 1) | 0x01 ), 1])) + 'P'
        self.ser.flushInput()
        self.ser.write(data)
        read = self.ser.read(size=1)
        if (read == ''):
            self.I2CError()
        return ord(read)
    
    def write_byte_data(self, address, register, value):
        data = 'S' + "".join(map(chr, [((address << 1) & 0xfe ), 2, register, value ])) + 'P'
        w = self.ser.write(data)

    def read_byte_data(self, address, register):
        self.write_byte(address, register)
        return self.read_byte(address)

    def write_word_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_word_data(self, address, register):
        data = 'S' + "".join(map(chr, [((address << 1) & 0xfe ), 1, register ])) + 'S' + "".join(map(chr, [((address << 1) | 0x01 ), 2 ])) + 'P'
        self.ser.flushInput()
        self.ser.write(data)
        read = self.ser.read(size=2)
        if (read == ''):
            self.I2CError()
        return ((ord(read[0])) + (ord(read[1])<<8))

    def write_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_block_data(self, address, register):
        raise NotImplementedError()

    def write_i2c_block(self, address, value):
        raise NotImplementedError()
  
    def read_i2c_block(self, address):
        raise NotImplementedError()

    def write_i2c_block_data(self, address, register, value):
        raise NotImplementedError()
    
    def read_i2c_block_data(self, address, register, length = 1):
        raise NotImplementedError()

class MachineDriver(Driver):
    def __init__(self, bus):
        self.bus = bus
        self.driver_type = "machine"

    def get_driver(self):
        return self.driver_type

    def write_byte(self, address, value, stop=True):
        return self.bus.writeto(address, struct.pack("B", value), stop=stop)
    
    def read_byte(self, address, stop=True):
        return struct.unpack("B", self.bus.readfrom(address, 1, stop=stop))[0]
    
    def write_byte_data(self, address, register, value):
        self.bus.writeto_mem(address, register, struct.pack("B", value))
    
    def read_byte_data(self, address, register):
        return struct.unpack("B", self.bus.readfrom_mem(address, register, 1))[0]
    
    def write_word_data(self, address, register, value):
        self.bus.writeto_mem(address, register, struct.pack("H", value))
    
    def read_word_data(self, address, register):
        return struct.unpack("H", self.bus.readfrom_mem(address, register, 2))[0]
    
    def write_block_data(self, address, register, value):
        data = b''
        for b in value:
            data += struct.pack("B", b)
        self.bus.writeto_mem(address, register, data)
    
    def read_block_data(self, address, register):
        return self.bus.readfrom(address, register, 32)

    def write_i2c_block(self, address, value):
        data = b''
        for b in value:
            data += struct.pack("B", b)
        return self.bus.writeto(address, data)

    def read_i2c_block(self, address, length):
        return self.bus.readfrom(address, length)

    def write_i2c_block_data(self, address, register, value):
        data = b''
        for b in value:
            data += struct.pack("B", b)
        self.bus.writeto_mem(address, register, data)
    
    def read_i2c_block_data(self, address, register, length=1):
        return self.bus.readfrom_mem(address, register, length)

    def get_driver(self):
        return self.driver_type

DRIVER = None


def load_driver(**kwargs):
    device = kwargs.get("device", None)
    port = kwargs.get("port", None)

    if device == "hid" or device == None:
        try:
            import hid
            try:
                h = hid.device()
                h.open(0x10C4, 0xEA90) # Try Connect HID # TODO: za none
                
                h.write([0x01, 0x01]) # Reset Device for cancelling all transfers and reset configuration
                h.close()
                return HIDDriver(str(port)) # We can use this connection
            except IOError:
                pass
        except ImportError:
            pass
            

    if (device == "smbus" or device == None) and (port is not None):
        try:
            import smbus
            return SMBusDriver(port, smbus.SMBus(int(port)))
        except ImportError:
            pass
            
    if device == "serial" or device == None:
            try:
                if port == None:
                    serial_port = "/dev/ttyUSB0"
                else:
                    serial_port = str(port)
                import serial
                return SerialDriver(serial_port)
            except ImportError:
                pass
       
    if ((device == "machine") or (kwargs.get("freq", None) != None)) and (port != None):
        from machine import I2C

        freq = kwargs.get("freq", None)
        if freq == None:
            freq = 100000
        return MachineDriver(I2C(port, freq=freq))
    
    raise RuntimeError("Failed to load I2C driver")


def init(**kwargs):
    DRIVER = load_driver(**kwargs)
    self.driver_type = None


def write_byte(address, value):
    return DRIVER.write_byte(address, value)
    

def read_byte(address):
    return DRIVER.read_byte(address)


def write_byte_data(address, register, value):
    return DRIVER.write_byte_data(address, register, value)


def read_byte_data(address, register):
    return DRIVER.read_byte_data(address, register)


def write_word_data(address, register, value):
    return DRIVER.write_word_data(address, register, value)


def read_word_data(address, register):
    return DRIVER.read_word_data(address, register)


def write_block_data(address, register, value):
    return DRIVER.write_block_data(address, register, value)


def read_block_data(address, register):
    return DRIVER.read_block_data(address, register)

def write_i2c_block_data(self, address, register, value):
    return DRIVER.write_i2c_block_data(self, address, register, value)

def read_i2c_block_data(self, address, register, length):
    return DRIVER.read_i2c_block_data(self, address, register, length)