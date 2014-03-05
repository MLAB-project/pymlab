#!/usr/bin/python
# -*- coding: utf-8 -*-
"""fry.tests.runtime module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import logging
logging.basicConfig(level = logging.DEBUG)


import unittest
import cStringIO as StringIO

try:
    from pymlab import config
except ImportError:
    config = None


@unittest.skipIf(config is None, "Could not import `pymlab.config`.")
class ConfigTestCase(unittest.TestCase):
    def test_load_python_00(self):
        cfg = config.Config()
        cfg.load_python("""
i2c = {
    "port": 5,
}

bus = [
]
        """)
    
    def test_load_python_01(self):
        cfg = config.Config()
        cfg.load_python("""
i2c = {
    "port": 5,
}

bus = [
    { "type": "mag01", "address": 0x68 },
    { "type": "sht25" }
]
        """)

    def test_load_python_02(self):
        cfg = config.Config()
        cfg.load_python("""
i2c = {
    "port": 5,
}

bus = [
    { "type": "i2chub", "address": 0x70, "children": [ {"type": "mag01", "channel": 0}, {"type": "mag01", "channel": 1}, ] },
    { "type": "mag01", "address": 0x68 }
]
        """)
    
    def test_load_python_03(self):
        cfg = config.Config()
        cfg.load_python("""
i2c = {
    "port": 5,
}

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

    def test_load_python_04(self):
        cfg = config.Config()
        cfg.load_python("""
i2c = {
    "port": 1,
}

bus = [
    {
        "type": "altimet01",
        "name": "alt",
    },
]

        """)



def main():
    unittest.main()


if __name__ == "__main__":
    main()

