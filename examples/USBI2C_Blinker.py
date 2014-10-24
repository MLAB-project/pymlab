#!/usr/bin/python
import hid
import time
from time import sleep
import os, sys

def init():
    global h
    print "Opening device"
    h = hid.device()
    h.open(0x10C4, 0xEA90)

    print "Manufacturer: %s" % h.get_manufacturer_string()
    print "Product: %s" % h.get_product_string()
    print "Serial No: %s" % h.get_serial_number_string()

    h.write([0x02, 0xFF, 0xFF, 0x00, 0x00])
    sleep( 1.00 )


def light(timea):
    global h
    h.write([0x04, 0xFF, 0xFF])
    print timea
    time.sleep(timea)
    return 0

def dark(timea):
    global h
    h.write([0x04, 0x00, 0xFF])
    print timea
    time.sleep(timea)
    return 0

def neon():
    light(1.15)
    dark(0.02)
    light(3.24)
    dark(0.01)
    light(1.12)
    dark(0.2)
    light(0.8)
    dark(0.8)
    light(0.45)
    dark(0.11)
    light(1.0)
    dark(0.2)
    light(3.0)
    dark(0.1)
    light(4.0)
    dark(0.4)
    light(5)
    dark(0.04)
    light(0.8)
    dark(0.04)
    light(1)
    dark(0.01)
    light(2)


def blik():
    light(1)
    dark(0.8)

def main():
    init()
    try:
        while 1:
            #blik()
            neon()

        print "Closing device"
        h.close()

    except IOError, ex:
        print ex

    print "Done"


if __name__ == "__main__":
    main()
