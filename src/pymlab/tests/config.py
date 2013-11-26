#!/usr/bin/python
# -*- coding: utf-8 -*-
"""fry.tests.runtime module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import unittest
import cStringIO as StringIO

try:
    from pymlab import config
except ImportError:
    config = None
from pymlab.sensors import Device


@unittest.skipIf(config is None, "Could not import `pymlab.config`.")
class ConfigTestCase(unittest.TestCase):
    def test_load_python_00(self):
        cfg = config.Config()
        cfg.load_python("""
port = 5

bus = [
]
        """)

    def test_load_python_01(self):
        cfg = config.Config()
        cfg.load_python("""
port = 5

bus = [
    { "type": "mag01", "address": 0x68 },
    { "type": "sht25" }
]
        """)

    def test_load_python_02(self):
        cfg = config.Config()
        cfg.load_python("""
port = 5

bus = [
    { "type": "i2chub", "address": 0x70, "children": [ {"type": "mag01", "channel": 0}, {"type": "mag01", "channel": 1}, ] },
    { "type": "mag01", "address": 0x68 }
]
        """)
    
    def test_load_python_03(self):
        cfg = config.Config()
        cfg.load_python("""
port = 1

bus = [
    {
        "type": "i2chub",
        "address": 0x72,
        
        "children": [
            {
                "type": "i2chub",
                "address": 0x70,
                "channel": 1,
                
                "children": [
                    { "type": "sht25", "channel": 2, },
                    { "type": "mag01", "channel": 2, },
                ],
            },
        ],
    },
]

        """)

    def _test_load_python(self, driver_name):
        cfg = config.Config()
        cfg.load_python("""
port = 1

bus = [
    {{ "type": "{}", "name": "dev", }},
]

        """.format(driver_name))
        
        dev = cfg.get_device("dev")
        self.assertIsInstance(dev, Device)
    
    def test_load_python_altimet01(self):
        self._test_load_python("altimet01")
    
    def test_load_python_sht25(self):
        self._test_load_python("sht25")
    
    def test_load_python_mag01(self):
        self._test_load_python("mag01")
    
    def test_load_python_i2chub(self):
        self._test_load_python("i2chub")
    
    def test_load_python_lts01(self):
        self._test_load_python("lts01")
    
    def test_load_python_alt01(self):
        self._test_load_python("alt01")


def main():
    unittest.main()


if __name__ == "__main__":
    main()

