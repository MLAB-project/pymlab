#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.config module.

Author: Jan Milík <milikjan@fit.cvut.cz>

This file contains reference to symbols which may apear in I2C network config string.

"""


import sys
import json
import logging

from . import utils
#from utils import obj_repr, PrettyPrinter
from pymlab.sensors import Bus, SimpleBus


LOGGER = logging.getLogger(__name__)


class Node(object):
    def __init__(self, config, address, name = None):
        self.config  = config
        self.parent  = None
        self.channel = None
        self.address = address
        self.name    = name

        config.add_node(self)

    def __repr__(self):
        return utils.obj_repr(self, self.address, self.name)

    def __pprint__(self, printer, level = 0):
        printer.write("%s  %d  %s" % (type(self).__name__, self.address, self.name, ))


class Config(object):
    """
    Example:

    >>> cfg = Config()
    >>> cfg.load_python("config_file.py")

    Contents of `config_file.py`:

    .. code-block:: python

        root = mult(
            address = 0x70,
            name    = "Multiplexer 1",
            children = {
                0x01: mult(
                    address = 0x72,
                    name    = "Multiplexer 2",
                    children = {
                        0x01: sens(
                            address = 0x68,
                            name    = "Sensor 2",
                        ),
                    },
                ),
                0x03: sens(
                    address = 0x68,
                    name    = "Sensor 1",
                ),
            },
        )

    """


    def __init__(self, **kwargs):
        self.drivers = {}
        self.i2c_config = {}
        self._bus = None

        self.init_drivers()
        self.config(**kwargs)

    @property
    def bus(self):
        if self._bus is None:
            self._bus = Bus(**self.i2c_config)
        return self._bus

    def init_drivers(self):
        from pymlab.sensors import lts, mag, sht, i2chub, altimet, acount, clkgen,\
                    imu, motor, atmega, gpio, bus_translators, light, thermopile,\
                    rps, adc, i2cpwm, i2cio, i2clcd, lioncell, rtc, lightning,\
                    windgauge, sdp3x, sps

        self.drivers = {
            "i2chub": i2chub.I2CHub,

            "lts01": lts.LTS01,
            "mag01": mag.MAG01,
            "rps01": rps.RPS01,
            "imu01_acc": imu.IMU01_ACC,
            "imu01_gyro": imu.IMU01_GYRO,
            "mpu6050": imu.MPU6050,
            "ICM20948" : imu.ICM20948,
            "sht25": sht.SHT25,
            "sht31": sht.SHT31,
            "altimet01": altimet.ALTIMET01,
            "SDP600": altimet.SDP6XX,
            "SDP610": altimet.SDP6XX,
            "SDP33": altimet.SDP3X,
            "acount02": acount.ACOUNTER02,
            "motor01": motor.MOTOR01,
            "clkgen01": clkgen.CLKGEN01,
            "atmega": atmega.ATMEGA,
            "I2CIO_TCA9535": gpio.I2CIO_TCA9535,
            "DS4520": gpio.DS4520,
            "TCA6416A": gpio.TCA6416A,
            "USBI2C_gpio": gpio.USBI2C_GPIO,
            "i2cspi": bus_translators.I2CSPI,
            "isl01": light.ISL01,
            "isl03": light.ISL03,
            "lioncell": lioncell.LIONCELL, #LION1CELL and LION2CELL
            "thermopile01": thermopile.THERMOPILE01,
            "i2cadc01": adc.I2CADC01,
            "vcai2c01": adc.VCAI2C01,
            "LTC2453": adc.LTC2453,
            "LTC2487": adc.LTC2487,
            "i2cpwm": i2cpwm.I2CPWM,
            "i2cio": i2cio.I2CIO,
            "i2clcd": i2clcd.I2CLCD,
            "rtc01": rtc.RTC01,
            "PCA9635": gpio.PCA9635,
            "LIGHTNING01A": lightning.AS3935,
            "WINDGAUGE03A": windgauge.WINDGAUGE03A,
            "SDP3x": sdp3x.SDP3x,
            "SPS30": sps.SPS30,
            "SEN5x": sps.SEN5x,
        }

    def get_device(self, name):
        return self.bus.get_device(name)

    def build_device(self, value, parent = None):
        if isinstance(value, list) or isinstance(value, tuple):
            if parent is None:
                result = Bus(**self.i2c_config)
            else:
                result = SimpleBus(parent)
            for child in value:
                result.add_child(self.build_device(child, result))
            return result

        if isinstance(value, dict):
            if "type" not in value:
                raise ValueError("Device dictionary doesn't have a \"type\" item.")

            try:
                fn = self.drivers[value["type"]]
            except KeyError:
                raise ValueError("Unknown device type: {!r}".format(value["type"]))

            kwargs = dict(value)
            kwargs.pop("type")

            children = kwargs.pop("children", [])

            result = fn(**kwargs)

            for child in children:
                result.add_child(self.build_device(child, result))

            return result

        if isinstance(value, Device):
            return value

        raise ValueError("Cannot create a device from: {!r}!".format(value))

    def config(self, **kwargs):
        self.i2c_config = kwargs.get("i2c", {})
        self._bus = self.build_device(kwargs.get("bus", []))

    def load_python(self, source):
        local_vars = {
            "cfg":  self,
            #"mult": self._mult,
            #"sens": self._sens,
            #"mult": Multiplexer,
            #"sens": Sensor,
        }
        exec(source, globals(), local_vars)
        #self.port = local_vars.get("port", self.port)

        self.i2c_config = local_vars.get("i2c", {})

        bus = self.build_device(local_vars.get("bus", []))
        if not isinstance(bus, Bus):
            LOGGER.warning(
                "Top-level device in the configuration is a "
                "%s and not a bus as expected. Use python list to "
                "denote a bus.",
                "None" if bus is None else type(bus).__name__)
        self._bus = bus

    def load_file(self, file_name):
        if file_name.endswith(".py"):
            with open(file_name, "r") as f:
                return self.load_python(f.read())
        raise ValueError("Unknown file type: {!r}".format(file_name))

    def initialize(self):
        self.bus.initialize()
        return self._bus


def main():
    cfg = Config()

    for file_name in sys.argv[1:]:
        cfg.load_python(file_name)

    pp = PrettyPrinter()
    pp.format(cfg.root_node)
    pp.writeln()

    for name, node in cfg.named_nodes.iteritems():
        print("%s: %r" % (name, node ))
    #print repr(cfg.root_node)


if __name__ == "__main__":
    main()
