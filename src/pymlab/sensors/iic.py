#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors.iic module.

Author: Jan Milik <milikjan@fit.cvut.cz>
"""
import time
import struct
import logging


LOGGER = logging.getLogger(__name__)

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

    """
    Key to symbols
    ==============

    S     (1 bit) : Start bit
    P     (1 bit) : Stop bit
    Rd/Wr (1 bit) : Read/Write bit. Rd equals 1, Wr equals 0.
    A, NA (1 bit) : Accept and reverse accept bit. 
    Addr  (7 bits): I2C 7 bit address. Note that this can be expanded as usual to 
                    get a 10 bit I2C address.
    Comm  (8 bits): Command byte, a data byte which often selects a register on
                    the device.
    Data  (8 bits): A plain data byte. Sometimes, I write DataLow, DataHigh
                    for 16 bit data.
    Count (8 bits): A data byte containing the length of a block operation.

    [..]: Data sent by I2C device, as opposed to data sent by the host adapter.

    More detail documentation is at https://www.kernel.org/doc/Documentation/i2c/smbus-protocol
    """

    def __init__(self, port, smbus):
        self.port = port
        self.smbus = smbus
        self.driver_type = 'smbus'
    
    def write_byte(self, address, value):
        """
        SMBus Send Byte:  i2c_smbus_write_byte()
        ========================================

        This operation is the reverse of Receive Byte: it sends a single byte
        to a device.  See Receive Byte for more information.

        S Addr Wr [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_BYTE
        """

        return self.smbus.write_byte(address, value)
    
    def read_byte(self, address):
        """
        SMBus Send Byte:  i2c_smbus_write_byte()
        ========================================

        This operation is the reverse of Receive Byte: it sends a single byte
        to a device.  See Receive Byte for more information.

        S Addr Wr [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_BYTE
        """
        return self.smbus.read_byte(address)
    
    def write_byte_data(self, address, register, value):
        """
        SMBus Read Byte:  i2c_smbus_read_byte_data()
        ============================================

        This reads a single byte from a device, from a designated register.
        The register is specified through the Comm byte.

        S Addr Wr [A] Comm [A] S Addr Rd [A] [Data] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_BYTE_DATA
        """
        return self.smbus.write_byte_data(address, register, value)
    
    def read_byte_data(self, address, register):
        """
        SMBus Read Byte:  i2c_smbus_read_byte_data()
        ============================================

        This reads a single byte from a device, from a designated register.
        The register is specified through the Comm byte.

        S Addr Wr [A] Comm [A] S Addr Rd [A] [Data] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_BYTE_DATA
        """
        return self.smbus.read_byte_data(address, register)

    def write_word_data(self, address, register, value):
        """
        SMBus Write Word:  i2c_smbus_write_word_data()
        ==============================================

        This is the opposite of the Read Word operation. 16 bits
        of data is written to a device, to the designated register that is
        specified through the Comm byte. 

        S Addr Wr [A] Comm [A] DataLow [A] DataHigh [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_WORD_DATA

        Note the convenience function i2c_smbus_write_word_swapped is
        available for writes where the two data bytes are the other way
        around (not SMBus compliant, but very popular.)
        """
        return self.smbus.write_word_data(address, register, value)
    
    def read_word_data(self, address, register):
        """
        SMBus Read Word:  i2c_smbus_read_word_data()
        ============================================

        This operation is very like Read Byte; again, data is read from a
        device, from a designated register that is specified through the Comm
        byte. But this time, the data is a complete word (16 bits).

        S Addr Wr [A] Comm [A] S Addr Rd [A] [DataLow] A [DataHigh] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_WORD_DATA

        Note the convenience function i2c_smbus_read_word_swapped is
        available for reads where the two data bytes are the other way
        around (not SMBus compliant, but very popular.)
        """
        return self.smbus.read_word_data(address, register)
    
    def write_block_data(self, address, register, value):
        """
        SMBus Block Write:  i2c_smbus_write_block_data()
        ================================================

        The opposite of the Block Read command, this writes up to 32 bytes to 
        a device, to a designated register that is specified through the
        Comm byte. The amount of data is specified in the Count byte.

        S Addr Wr [A] Comm [A] Count [A] Data [A] Data [A] ... [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_BLOCK_DATA
        """
        return self.smbus.write_block_data(address, register, value)
    
    def read_block_data(self, address, register):
        """
        SMBus Block Read:  i2c_smbus_read_block_data()
        ==============================================

        This command reads a block of up to 32 bytes from a device, from a 
        designated register that is specified through the Comm byte. The amount
        of data is specified by the device in the Count byte.

        S Addr Wr [A] Comm [A] 
                   S Addr Rd [A] [Count] A [Data] A [Data] A ... A [Data] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_BLOCK_DATA
        """
        return self.smbus.read_block_data(address, register)

    def block_process_call(self, address, register, value):
        """
        SMBus Block Write - Block Read Process Call
        ===========================================

        SMBus Block Write - Block Read Process Call was introduced in
        Revision 2.0 of the specification.

        This command selects a device register (through the Comm byte), sends
        1 to 31 bytes of data to it, and reads 1 to 31 bytes of data in return.

        S Addr Wr [A] Comm [A] Count [A] Data [A] ...
                                     S Addr Rd [A] [Count] A [Data] ... A P

        Functionality flag: I2C_FUNC_SMBUS_BLOCK_PROC_CALL
        """
        return self.smbus.block_process_call(address, register, value)

    ### I2C transactions not compatible with pure SMBus driver
    def write_i2c_block(self, address, value):
        """
        Simple send transaction
        ======================

        This corresponds to i2c_master_send.

          S Addr Wr [A] Data [A] Data [A] ... [A] Data [A] P

        More detail documentation is at: https://www.kernel.org/doc/Documentation/i2c/i2c-protocol
        """
        raise NotImplementedError()
  
    def read_i2c_block(self, address, length):
        """
        Simple receive transaction
        ===========================

        This corresponds to i2c_master_recv

          S Addr Rd [A] [Data] A [Data] A ... A [Data] NA P

        More detail documentation is at: https://www.kernel.org/doc/Documentation/i2c/i2c-protocol
        """
	data=[]
        for k in range(length):
	    data.append(self.smbus.read_byte(address))
        return data
        raise NotImplementedError()

    def write_i2c_block_data(self, address, register, value):
        """
        I2C block transactions do not limit the number of bytes transferred
        but the SMBus layer places a limit of 32 bytes.

        I2C Block Write:  i2c_smbus_write_i2c_block_data()
        ==================================================

        The opposite of the Block Read command, this writes bytes to 
        a device, to a designated register that is specified through the
        Comm byte. Note that command lengths of 0, 2, or more bytes are
        supported as they are indistinguishable from data.

        S Addr Wr [A] Comm [A] Data [A] Data [A] ... [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_I2C_BLOCK
        """
        return self.smbus.write_i2c_block_data(address, register, value)
    
    def read_i2c_block_data(self, address, register, length):
        """
        I2C block transactions do not limit the number of bytes transferred
        but the SMBus layer places a limit of 32 bytes.

        I2C Block Read:  i2c_smbus_read_i2c_block_data()
        ================================================

        This command reads a block of bytes from a device, from a 
        designated register that is specified through the Comm byte.

        S Addr Wr [A] Comm [A] 
                   S Addr Rd [A] [Data] A [Data] A ... A [Data] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_I2C_BLOCK
        """
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
        LOGGER.warning("CP2112 Byte Read Error...")
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
        LOGGER.warning("CP2112 Byte Data Read Error...")
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
        LOGGER.warning("CP2112 Word Read Error...")
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
        LOGGER.warning("CP2112 Byte Data Read Error...")
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
        LOGGER.debug("Serial port initialized. Testing connectivity")
        self.ser.flushInput()
        self.ser.write('IP')
        if (self.ser.read() == ''):
            LOGGER.info("Serial to I2C converter is not connected")
            raise IOError()

        else:
            LOGGER.info("Serial to I2C converter connected sucessfully")

    
    def I2CError(self):
        raise IOError()

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
            LOGGER.info("Serial to I2C converter is disconnected")
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
            LOGGER.info("Serial to I2C converter is disconnected")
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



DRIVER = None


def load_driver(**kwargs):
    device = kwargs.get("device", None)
    port = kwargs.get("port", None)

    if device == "hid" or device == None:
        try:
            LOGGER.info("Loading HID driver...")
            import hid
            LOGGER.info("Initiating HID driver...")
            try:
                h = hid.device()
                h.open(0x10C4, 0xEA90) # Try Connect HID # TODO: za none
                LOGGER.info("Using HID '%s' device with serian number: '%s' from '%s'." %(h.get_product_string(), h.get_serial_number_string(), h.get_manufacturer_string()))
                h.write([0x01, 0x01]) # Reset Device for cancelling all transfers and reset configuration
                h.close()
                return HIDDriver(str(port)) # We can use this connection
            except IOError:
                LOGGER.warning("HID device does not exist, we will try SMBus directly...")
        
        except ImportError:
            LOGGER.warning("HID driver cannot be imported, we will try SMBus driver...")


    if (device == "smbus" or device == None) and (port is not None):
        try:
            import smbus
            LOGGER.info("Loading SMBus driver...")
            return SMBusDriver(port, smbus.SMBus(int(port)))
        except ImportError:
            LOGGER.warning("Failed to import 'smbus' module. SMBus driver cannot be loaded.")
    #else:
    #    LOGGER.warning("SMBus port not specified, skipping trying to load smbus driver.")
    

    if device == "serial" or device == None:
            try:
                if port == None:
                    serial_port = "/dev/ttyUSB0"
                else:
                    serial_port = str(port)
                LOGGER.info("Loading SERIAL driver...")
                import serial
                return SerialDriver(serial_port)

            except ImportError:
                    LOGGER.warning("Failed to import 'SC18IM700' driver. I2C232 driver cannot be loaded for port %s." %(serial_port))
       
    
    raise RuntimeError("Failed to load I2C driver. Enable logging for more details.")


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

def main():
    print __doc__


if __name__ == "__main__":
    main()

