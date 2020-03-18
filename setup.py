#!/bin/env/python

import distutils.cmd
import distutils.log
from distutils.core import setup, Extension
import os
import sys
from setuptools import find_packages
from glob import glob
import subprocess
import platform
import setuptools.command.build_py

ANTLR_VERSION = "4.8"
ANTLR_RT = "antlr4-python3-runtime == {}".format(ANTLR_VERSION)

def find_antlr():
    try:
        ANTLR_JAR = os.environ["ANTLR_JAR"]
    except KeyError:
        system = platform.system()
        jar = "antlr-" + ANTLR_VERSION + "-complete.jar"

        # Try to guess installation path based on suggestions in ANTLR documentation.
        if system in ["Darwin", "Linux"]:
            install_path = "/usr/local/lib/"
        elif system == "Windows":
            install_path = "C:\\Javalib\\"
        else:
            # Unknown operating system.
            install_path = ""

        ANTLR_JAR = os.path.join(install_path, jar)

    if not os.path.exists(ANTLR_JAR):
        raise FileNotFoundError("ANTLR4 not found: {0}".format(ANTLR_JAR))

    return ANTLR_JAR

ANTLR_JAR = find_antlr()


class AntrlAutogen(distutils.cmd.Command):
    """Custom command to autogenerate Python code using ANTLR."""

    description = "generate python code using antlr"

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run ANTLR."""
        antlr4 = ["java", "-Xmx500M", "-cp", ANTLR_JAR, "org.antlr.v4.Tool"]
        check_version(antlr4)
        a2l_grammar = os.path.join("pya2l", "a2l.g4")
        aml_grammar = os.path.join("pya2l", "aml.g4")
        arguments = [a2l_grammar, aml_grammar, "-Dlanguage=Python3"]
        self.announce(" ".join(antlr4 + arguments), level=distutils.log.INFO)
        subprocess.check_call(antlr4 + arguments)
        clean()


def check_version(command):
    """Check that ANTLR4 is the correct version."""
    out = subprocess.check_output(command).decode(sys.stdout.encoding)
    antlr_version = out.split("\n")[0].split(" ")[-1]

    if not antlr_version == ANTLR_VERSION:
        found = "Wrong ANTLR version: {}".format(antlr_version) + "."
        required = "pyA2L requires {}".format(ANTLR_VERSION) + "."

        raise ValueError(found + required)


def clean():
    """Remove unneeded files."""
    tokens = glob(os.path.join("pya2l", "*tokens"))
    interp = glob(os.path.join("pya2l", "*interp"))
    listener = glob(os.path.join("pya2l", "*Listener.py"))

    for unneeded in tokens + interp + listener:
        os.remove(unneeded)


class CustomBuildPy(setuptools.command.build_py.build_py):
    """Extended build_py which also runs ANTLR."""

    def run(self):
        self.run_command("antlr")
        super().run()


install_reqs = [ANTLR_RT, "mako", "six", "SQLAlchemy", "sortedcontainers"]

with open(os.path.join("pya2l", "version.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[-1].strip().strip('"')
            break

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pya2l",
    version=version,
    description="A2L for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Christoph Schueler",
    author_email="cpu12.gems@googlemail.com",
    url="https://www.github.com/Christoph2/pyA2L",
    cmdclass={"antlr": AntrlAutogen, "build_py": CustomBuildPy,},
    packages=find_packages(),
    install_requires=install_reqs,
    tests_require=["pytest", "pytest-runner"],
    test_suite="pya2l.tests",
    license="GPLv2",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
