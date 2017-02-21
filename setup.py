#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import sys
from os import path
from glob import glob

name = 'urwid_sparkwidgets'
setup(name=name,
      version='0.0.1',
      description=u'A set of sparkline-ish widgets for urwid',
      author='Ton Cebzanov',
      author_email='tonycpsu@gmail.com',
      url='https://github.com/tonycpsu/urwid-sparkline',
      classifiers=[
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Intended Audience :: Developers'],
      packages=['urwid_sparkline'],
      data_files=[('share/doc/%s' % name, ['LICENSE','README.md']),
              ],
      install_requires = ['urwid',
                          'urwid_utils']
     )
