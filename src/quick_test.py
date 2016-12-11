
import logging

from pymlab import config

logging.basicConfig(level = logging.DEBUG)

cfg = config.Config()
cfg.load_file("../config.py")

