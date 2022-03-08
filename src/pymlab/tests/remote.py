#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pymlab.sensors.iic import load_driver


class RemoteDriverTestCase(unittest.TestCase):
    def test_dummy_driver(self):
        d = load_driver(
            device="dummy"
        )
        self.assertEqual(d.read_byte(0), 0xaa)

    def test_remote_driver(self):
        d = load_driver(
            device="remote",
            host=[], # will run the server locally
            remote_device={"device": "dummy"}
        )
        self.assertEqual(d.read_byte(0), 0xaa)
        d.close()


def main():
    unittest.main()


if __name__ == "__main__":
    main()

