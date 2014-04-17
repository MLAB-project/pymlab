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
    description      = 'Personal toolbox for unix programs.',
    long_description = pymlab.__doc__,
    url              = 'https://github.com/MLAB-project/MLAB-I2c-modules',
    
    #packages    = ['pymlab', 'pymlab.sensors', 'pymlab.tests', ],
    packages    = find_packages("src"),
    package_dir = {'': 'src'},
    # py_modules  = ['nmapps'],
    provides    = ['pymlab'],
    keywords    = 'library unix',
    license     = 'Lesser General Public License v3',
    
    #scripts     = ['src/scripts/eggimp.py', ],
    
    #entry_points = {
    #    "console_scripts": ["nmapps = nmapps.tool:main", ],
    #},
    
    test_suite = 'pymlab.tests',
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        # 'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)

