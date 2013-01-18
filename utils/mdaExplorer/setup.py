#!/usr/bin/env python

# $Id$

"""
Support for EPICS MDA files

use this file to install the mda support library with::

   ./setup.py install

"""
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='mdalib',
    version='2.0',
    author='Tim Mooney',
    author_email = 'mooney@aps.anl.gov',
    description = 'MDA support library',
    license = 'EPICS',
    py_modules = ['f_xdrlib', 'mda_f'],
    #entry_points = {
    #    'nose.plugins.0.10': [
    #        'example = plug:ExamplePlugin'
    #        ]
    #s    }

    )
