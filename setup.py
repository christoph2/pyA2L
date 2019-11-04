#!/bin/env/python

from distutils.core import setup, Extension
import os
import sys
from setuptools import find_packages
from glob import glob

ANTLR_VERSION = '4.7.2'
ANTLR_RT = "antlr4-python3-runtime=={}".format(ANTLR_VERSION) if sys.version_info.major == 3 else "antlr4-python2-runtime=={}".format(ANTLR_VERSION)


install_reqs = [ANTLR_RT, 'mako', 'six', 'SQLAlchemy']

if sys.version_info.major == 2 or (sys.version_info.major == 3 and sys.version_info.minor < 4):
    install_reqs.extend(['enum34', 'mock'])

with open(os.path.join('pya2l', 'version.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[-1].strip().strip('"')
            break

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'pya2l',
    version=version,
    description = "A2L for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    tests_require=["pytest", "pytest-runner"],
    test_suite="pya2l.tests",
    license='GPLv2',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

)

