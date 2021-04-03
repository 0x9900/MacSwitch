#!/usr/bin/env python3.7
#
import sys

from setuptools import setup, find_packages

__doc__ = """
## MacSwitch

Companion program for the Antenna Switch
https://github.com/0x9900/AntennaSwitch

For more information check https://0x9900.com/remote-controlled-antenna-switch/

"""

__author__ = "Fred C. (W6BSD)"
__version__ = '0.1.6'
__license__ = 'BSD'

py_version = sys.version_info[:2]
if py_version < (3, 5):
  raise RuntimeError('MacSwitch requires Python 3.5 or later')

setup(
  name='MacSwitch',
  version=__version__,
  description='Remote Antenna Switch',
  long_description=__doc__,
  long_description_content_type='text/markdown',
  url='https://github.com/0x9900/AntennaSwitch/',
  license=__license__,
  author=__author__,
  author_email='w6bsd@bsdworld.org',
  py_modules=['asmac'],
  install_requires=['PyQt5', 'requests'],
  entry_points = {
    'console_scripts': ['macswitch = asmac:main'],
  },
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Topic :: Communications :: Ham Radio',
  ],
)
