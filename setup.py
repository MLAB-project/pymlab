#!/usr/bin/python
# -*- coding: utf8 -*-

from setuptools import setup, find_packages
import sys
import os
import os.path as path


os.chdir(path.realpath(path.dirname(__file__)))
sys.path.insert(1, 'src')
import pymlab


setup(
    name             = 'pymlab',
    version          = pymlab.__version__,
    author           = 'Jan Milík',
    author_email     = 'milikjan@fit.cvut.cz',
    description      = 'Toolbox for interfacing I2C sensors.',
    long_description = pymlab.__doc__,
    url              = 'https://github.com/MLAB-project/pymlab',
    
    #packages    = ['pymlab', 'pymlab.sensors', 'pymlab.tests', ],
    packages    = find_packages("src"),
    package_dir = {'': 'src'},
    provides    = ['pymlab'],
    install_requires = [ 'hidapi' ],
    keywords = ['TWI', 'IIC', 'I2C', 'USB', 'sensors', 'drivers'],
    license     = 'Lesser General Public License v3',
    download_url = 'https://github.com/MLAB-project/pymlab/archive/refs/heads/master.zip',
    
    test_suite = 'pymlab.tests',
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: Czech',
        # 'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)

