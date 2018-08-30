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
    version='2013-02',
    author='Tim Mooney',
    author_email = 'mooney@aps.anl.gov',
    description = 'MDA support library',
    long_description = """
    Python support library for EPICS synApps MDA-format data files
    
    Install the Python mda support library:
    
        cd synApps/support/utils/mdaPythonUtils
        python ./setup.py install
        # -or-
        pip install .
    
    """,
    license = 'EPICS',
    url = 'https://github.com/EPICS-synApps/utils/tree/master/mdaPythonUtils',
    py_modules = ['f_xdrlib', 'mda'],
    )
