#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sensors.iic module.

Author: Jan Milik <milikjan@fit.cvut.cz>
"""
import time
import struct
import logging
import six
import sys
import subprocess
import ast


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

    def scan_bus(self):
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
        print(smbus)
        self.smbus = smbus
        self.driver_type = 'smbus'

    @property
    def driver(self):
        return self.smbus

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
        return self.smbus.write_i2c_block(address, value)

    def read_i2c_block(self, address, length):
        """
        Simple receive transaction
        ===========================

        This corresponds to i2c_master_recv

          S Addr Rd [A] [Data] A [Data] A ... A [Data] NA P

        More detail documentation is at: https://www.kernel.org/doc/Documentation/i2c/i2c-protocol
        """
        return self.smbus.read_i2c_block(address, length)

    def write_i2c_block_data(self, address, register, value):
        """
        I2C block transactions do not limit the number of bytes transferred
        but the SMBus layer places a limit of 32 bytes.

        I2C Block Write:  i2c_smbus_write_i2c_block_data()
        ==================================================

        The opposite of the Block Read command, this writes bytes to
        a device, to a designated register that is specified through the
        Comm byte. Note that command lengths of 0, 2, or more bytes are
        seupported as they are indistinguishable from data.

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

    def scan_bus(self, verbose = False):
        devices = []
        for addr in range(128):
            out = self.smbus.read_byte(addr)
            if out > 0:
                devices += [addr]
            if verbose:
                if addr % 0x0f == 0:
                    print("", end = '')
                    print(hex(addr)+":", end = '')
                if out > 0:
                    print(hex(addr))
                else:
                    print(" -- ", end = '')

        print("")
        return devices


class HIDDriver(Driver):
    def __init__(self,**kwargs):
        import hid

        serial = kwargs.get('serial', None)
        if serial: serial = six.text_type(serial)

        self.driver_type = 'hid'
        self.h = hid.device()
        self.h.open(0x10C4, 0xEA90, serial) # Connect HID again after enumeration
        self.h.write([0x02, 0xFF, 0x00, 0x00, 0x00])  # Set GPIO to Open-Drain
        for k in range(3):      # blinking LED
            self.h.write([0x04, 0x00, 0xFF])
            time.sleep(0.05)
            self.h.write([0x04, 0xFF, 0xFF])
            time.sleep(0.05)

        self.gpio_direction = 0x00   # 0 - input, 1 - output
        self.gpio_pushpull  = 0x00   # 0 - open-drain, 1 - push-pull
        self.gpio_special   = 0x00   # only on bits 0-2,  0 standard gpio, 1 special function as LED, CLK out
        self.gpio_clockdiv  = 0x00   # see manual for more info..

        self.DATA_READ_REQUEST = 0x10
        self.DATA_WRITE_READ_REQUEST = 0x11
        self.DATA_READ_FORCE_SEND = 0x12
        self.DATA_READ_RESPONSE = 0x13
        self.DATA_WRITE = 0x14
        self.TRANSFER_STATUS_REQUEST = 0x15
        self.TRANSFER_STATUS_RESPONSE = 0x16
        self.CACEL_TRANSFER = 0x17


        if kwargs.get('led', True):     # Set GPIO to RX/TX LED
            self.gpio_direction = 0x02
            self.gpio_pushpull  = 0xFF
            self.gpio_special   = 0xFF

        self.h.write([0x02, self.gpio_direction, self.gpio_pushpull, self.gpio_special, self.gpio_clockdiv])  # initialize GPIO

        # Set SMB Configuration (AN 495)
        self.h.write([0x06, 0x00, 0x01, 0x86, 0xA0, 0x02, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x01, 0x00, 0x0F])

    def I2CError(self):
        self.h.write([0x01, 0x01]) # Reset Device for cancelling all transfers and reset configuration
        self.h.close()
        time.sleep(3)   # Give a time to OS for release the BUS
        raise IOError()

    def write_hid(self, data):
        self.h.write(data)

    def read_hid(self, len):
        return self.h.read(len)

    def get_handler(self):
        return h

    # WARNING ! - CP2112 does not support I2C address 0
    def write_byte(self, address, value):
        """
        SMBus Send Byte:  i2c_smbus_write_byte()
        ========================================

        This operation is the reverse of Receive Byte: it sends a single byte
        to a device.  See Receive Byte for more information.

        S Addr Wr [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_BYTE
        """
        return self.h.write([self.DATA_WRITE, address<<1, 0x01, value]) # Data Write Request

    def read_byte(self, address):
        """
        SMBus Send Byte:  i2c_smbus_write_byte()
        ========================================

        This operation is the reverse of Receive Byte: it sends a single byte
        to a device.  See Receive Byte for more information.

        S Addr Wr [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_BYTE
        """
        self.h.write([self.DATA_READ_REQUEST, address<<1, 0x00, 0x01]) # Data Read Request

        for k in range(10):
            self.h.write([self.TRANSFER_STATUS_REQUEST, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                self.h.write([self.DATA_READ_FORCE_SEND, 0x00, 0x01]) # Data Read Force
                response = self.h.read(4)
                return response[3]
        LOGGER.warning("CP2112 Byte Read Error...")
        self.I2CError()

    def write_byte_data(self, address, register, value):
        """
        SMBus Read Byte:  i2c_smbus_read_byte_data()
        ============================================

        This reads a single byte from a device, from a designated register.
        The register is specified through the Comm byte.

        S Addr Wr [A] Comm [A] S Addr Rd [A] [Data] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_BYTE_DATA
        """
        return self.h.write([self.DATA_WRITE, address<<1, 0x02, register, value]) # Data Write Request

    def read_byte_data(self, address, register):
        """
        SMBus Read Byte:  i2c_smbus_read_byte_data()
        ============================================

        This reads a single byte from a device, from a designated register.
        The register is specified through the Comm byte.

        S Addr Wr [A] Comm [A] S Addr Rd [A] [Data] NA P

        Functionality flag: I2C_FUNC_SMBUS_READ_BYTE_DATA
        """
        self.h.write([self.DATA_WRITE_READ_REQUEST, address<<1, 0x00, 0x01, 0x01, register]) # Data Write Read Request

        for k in range(10):
            self.h.write([self.TRANSFER_STATUS_REQUEST, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            #print "status",map(hex,response)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                self.h.write([self.DATA_READ_FORCE_SEND, 0x00, 0x01]) # Data Read Force
                response = self.h.read(4)
                #print "data ",map(hex,response)
                return response[3]
        LOGGER.warning("CP2112 Byte Data Read Error...")
        self.I2CError()

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
        return self.h.write([self.DATA_WRITE, address<<1, 0x03, register, value>>8, value & 0xFF]) # Word Write Request

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
        self.h.write([self.DATA_WRITE_READ_REQUEST, address<<1, 0x00, 0x02, 0x01, register]) # Data Write Read Request
        self.h.write([self.DATA_READ_FORCE_SEND, 0x00, 0x02]) # Data Read Force

        for k in range(10):             # Polling a data
            response = self.h.read(10)
            #print map(hex,response)
            #print "status ",response
            if (response[0] == 0x13) and (response[2] == 2):
                return (response[4]<<8)+response[3]
            #self.h.write([0x15, 0x01]) # Transfer Status Request
            self.h.write([self.DATA_WRITE_READ_REQUEST, address<<1, 0x00, 0x02, 0x01, register]) # Data Write Read Request
            self.h.write([self.DATA_READ_FORCE_SEND, 0x00, 0x02]) # Data Read Force
        LOGGER.warning("CP2112 Word Read Error...")
        self.I2CError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

    def write_i2c_block(self, address, value):
        """
        Simple send transaction
        ======================

        This corresponds to i2c_master_send.

          S Addr Wr [A] Data [A] Data [A] ... [A] Data [A] P

        More detail documentation is at: https://www.kernel.org/doc/Documentation/i2c/i2c-protocol
        """
        if (len(value) > 61):
            raise IndexError()
        data = [self.DATA_WRITE, address<<1, len(value)]  # Data Write Request (max. 61 bytes, hidapi allows max 8bytes transaction lenght)
        data.extend(value)
        return self.h.write(data) # Word Write Request
        self.I2CError()

    def read_i2c_block(self, address, length):
        """
        Simple receive transaction
        ===========================

        This corresponds to i2c_master_recv

          S Addr Rd [A] [Data] A [Data] A ... A [Data] NA P

        More detail documentation is at: https://www.kernel.org/doc/Documentation/i2c/i2c-protocol
        """
        self.h.write([self.DATA_READ_REQUEST, address<<1, 0x00, length]) # Data Read Request (60 bytes)

        for k in range(10):
            self.h.write([self.TRANSFER_STATUS_REQUEST, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            #print "response ",map(hex,response)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                #length = (response[5]<<8)+response[6]
                self.h.write([self.DATA_READ_FORCE_SEND, response[5], response[6]]) # Data Read Force
                data = self.h.read(length+3)
                #print "length ",length
                #print "data ",map(hex,data)
                return data[3:]
        LOGGER.warning("CP2112 Byte Data Read Error...")
        self.I2CError()

    def write_i2c_block_data(self, address, register, value):
        """
        I2C block transactions do not limit the number of bytes transferred
        but the SMBus layer places a limit of 32 bytes.

        I2C Block Write:  i2c_smbus_write_i2c_block_data()
        ==================================================

        The opposite of the Block Read command, this writes bytes to
        a device, to a designated register that is specified through the
        Comm byte. Note that command lengths of 0, 2, or more bytes are
        seupported as they are indistinguishable from data.

        S Addr Wr [A] Comm [A] Data [A] Data [A] ... [A] Data [A] P

        Functionality flag: I2C_FUNC_SMBUS_WRITE_I2C_BLOCK
        """
        if (len(value) > 61):
            raise IndexError()
        data = [self.DATA_WRITE, address<<1, len(value) + 1, register]  # Data Write Request (max. 61 bytes, hidapi allows max 8bytes transaction lenght)
        data.extend(value)
        return self.h.write(data) # Word Write Request
        self.I2CError()

    def read_i2c_block_data(self, address, register, length = 1):
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
        self.h.write([self.DATA_WRITE_READ_REQUEST, address<<1, 0x00, length, 0x01, register]) # Data Write Read Request

        for k in range(10):
            self.h.write([self.TRANSFER_STATUS_REQUEST, 0x01]) # Transfer Status Request
            response = self.h.read(7)
            #print "response ",map(hex,response)
            if (response[0] == 0x16) and (response[2] == 5):  # Polling a data
                #length = (response[5]<<8)+response[6]
                self.h.write([self.DATA_READ_FORCE_SEND, response[5], response[6]]) # Data Read Force
                data = self.h.read(length+3)
                #print "length ",length
                #print "data ",map(hex,data)
                return data[3:]
        LOGGER.warning("CP2112 Byte Data Read Error...")
        self.I2CError()


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


class RemoteDriver(Driver):
    def __init__(self, host, remote_device):
        import sys

        hosts = host if isinstance(host, list) else [host]
        self.host = hosts[-1] if len(hosts) > 0 else "local"

        cmd = [arg for h in hosts for arg in ["ssh", h]] \
              + ["python3", "-m", "pymlab.iic_server"]
        self.sp = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   text=True)

        self._remote_call('load_driver', remote_device)

    def close(self):
        self.sp.stdin.close()
        self.sp.wait()

    def _remote_call(self, method, *args):
        #line, errs = self.sp.communicate(repr((method,) + args) + '\n')
        self.sp.stdin.write(repr((method,) + args) + '\n')
        self.sp.stdin.flush()
        line = self.sp.stdout.readline().strip()

        try:
            reply = ast.literal_eval(line)
            assert isinstance(reply, dict) and 'good' in reply
        except Exception as e:
            raise RuntimeError('%s sent invalid reply %r' % (self.host, line))

        if reply.get('good', False):
            return reply.get('result', None)
        else:
            raise RuntimeError('%s raised exception: %s' \
                               % (self.host, reply.get('exception', '<missing>')))


    def write_byte(self, address, value):
        return self._remote_call('write_byte', address, value)

    def read_byte(self, address):
        return self._remote_call('read_byte', address)

    def write_byte_data(self, address, register, value):
        return self._remote_call('write_byte_data', address, register, value)

    def read_byte_data(self, address, register):
        return self._remote_call('read_byte_data', address, register)

    def write_word_data(self, address, register, value):
        return self._remote_call('write_word_data', address, register, value)

    def read_word_data(self, address, register):
        return self._remote_call('read_word_data', address, register)

    def write_block_data(self, address, register, value):
        return self._remote_call('write_block_data', address, register, value)

    def read_block_data(self, address, register):
        return self._remote_call('read_block_data', address, register)

    def scan_bus(self):
        return self._remote_call('scan_bus')


class DummyDriver(Driver):
    def __init__(self):
        self.driver_type = 'dummy'

    def get_handler(self):
        raise NotImplementedError()

    def write_byte(self, address, value):
        pass

    def read_byte(self, address):
        return 0xaa

    def write_byte_data(self, address, register, value):
        pass

    def read_byte_data(self, address, register):
        return 0xaa

    def write_word_data(self, address, register, value):
        pass

    def read_word_data(self, address, register):
        return 0xaaaa

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
    serial = kwargs.get("serial", None)
    print(kwargs)

    if (device == "hid") or (device == None):
        try:
            LOGGER.info("Loading HID driver...")
            import hid
            LOGGER.info("Initiating HID driver...")
            try:
                if serial:
                    if sys.version_info[0] >= 3:
                        serial = str(serial)
                    else:
                        serial = unicode(serial)

                h = hid.device()
                h.open(0x10C4, 0xEA90, serial) # Try Connect HID
                kwargs['serial'] = h.get_serial_number_string()
                LOGGER.info("Using HID with serial number: '%s' " %(h.get_serial_number_string()))
                #h.write([0x01, 0x01]) # Reset Device for cancelling all transfers and reset configuration
                #LOGGER.info("Reseting the USBI2C converter.")
                h.close()
                LOGGER.info("Waiting to reinit of the device...")
                time.sleep(1) # wait for system HID (re)mounting
                return HIDDriver(**kwargs) # We can use this connection

            except IOError:
                LOGGER.warning("HID device does not exist, we will try SMBus directly... (1)")

        except ImportError:
            LOGGER.warning("HID driver cannot be imported, we will try SMBus driver...(2)")

    if (device == "smbus2" or device == None):
        try:
            import smbus2
            smb = smbus2.SMBus(port)
            print("Loading Python smbus2 driver...", smb)
            LOGGER.info("Loading Python smbus2 driver...", smb)
            return SMBusDriver(port, smb)
        except ImportError:
            LOGGER.warning("Failed to import 'smbus2' module. SMBus driver cannot be loaded.")

    if (device == "smbus" or device == None) and (port is not None):
        try:
            import smbus
            LOGGER.info("Loading SMBus driver...")
            return SMBusDriver(port, smbus.SMBus(int(port)))
        except ImportError:
            LOGGER.warning("Failed to import Python 'smbus' module. We will try Python 'smbus2' as replacement.")

        try:
            import smbus2
            smb = smbus2.SMBus(port)
            print("Loading Python smbus2 driver...", smb)
            LOGGER.info("Loading Python smbus2 driver...", smb)
            return SMBusDriver(port, smb)
        except ImportError:
            LOGGER.warning("Failed to import 'smbus2' module. SMBus driver cannot be loaded.")

    if (device == "smbus" or device == "smbus2") and (port is None):
        LOGGER.error("Port of SMBus must be specified")

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

    if device == "remote":
        return RemoteDriver(kwargs['host'], kwargs.get("remote_device", {}))

    if device == "dummy":
        return DummyDriver()

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

def scan_bus(self):
    return DRIVER.scan_bus(self)

def main():
    print(__doc__)


if __name__ == "__main__":
    main()
