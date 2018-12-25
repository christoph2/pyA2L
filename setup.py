#!/bin/env/python

from distutils.core import setup, Extension
import os
import sys
from setuptools import find_packages
from glob import glob

ANTLR_VERSION = '4.7.2'
ANTLR_RT = "antlr4-python3-runtime=={}".format(ANTLR_VERSION) if sys.version_info.major == 3 else "antlr4-python2-runtime=={}".format(ANTLR_VERSION)


install_reqs = [ANTLR_RT, 'mako', 'six']

if sys.version_info.major == 2 or (sys.version_info.major == 3 and sys.version_info.minor < 4):
    install_reqs.extend(['enum34', 'mock'])

def packagez(base):
    return  ["%s%s%s" % (base, os.path.sep, p) for p in find_packages(base)]

setup(
    name = 'pya2l',
    version = '0.1.0',
    description = "A2L for Python",
    author = 'Christoph Schueler',
    author_email = 'cpu12.gems@googlemail.com',
    url = 'https://www.github.com/Christoph2/pyA2L',
    packages = find_packages(),
    install_requires = install_reqs,
    #entry_points = {
    #    'console_scripts': [
    #            'vd_exporter = pyA2L.catalogue.vd_exporter:main'
    #    ],
    #},
    #data_files = [
    #        ('pya2l/config', glob('pya2l/config/*.*')),
    #        ('pya2l/imagez', glob('pya2l/imagez/*.bin')),
    #],
    test_suite="pya2l.tests"
)

