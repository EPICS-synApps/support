#!/usr/bin/env python

# $Id$

import os
newpath = os.path.join('..', 'mdaPythonUtils/')
newpath = os.path.abspath(newpath)

print '''
The support to install the mda package 
has been relocated to this directory:\n\n\t%s

cd to that directory and run this again:

  python ./setup.py install
''' % newpath
