#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from itertools import chain
from pathlib import Path
from typing import Any
from typing import Dict

import setuptools.command.build_py
from pkg_resources import parse_requirements
from setuptools import Command


def _parse_requirements(filepath):
    with filepath.open() as text_io:
        requirements = list(parse_requirements(text_io))

    return requirements


ROOT_DIRPATH = Path(".")

BASE_REQUIREMENTS = _parse_requirements(ROOT_DIRPATH / "requirements.txt")
SETUP_REQUIREMENTS = _parse_requirements(ROOT_DIRPATH / "requirements.setup.txt")
TEST_REQUIREMENTS = _parse_requirements(ROOT_DIRPATH / "requirements.test.txt")
ANTLR_VERSION = next(req.specs[0][1] for req in BASE_REQUIREMENTS if req.project_name == "antlr4-python3-runtime")


def findAntlr():
    """Try to find the ANTLR .jar-file."""
    if os.environ.get("APPVEYOR"):
        classpath = r"antlr-{}-complete.jar".format(ANTLR_VERSION)
    else:
        classpath = os.getenv("CLASSPATH")
        classpath = classpath if classpath is not None else ""

    if "antlr" not in classpath.lower():
        print("ANTLR NOT in classpath!!!")
        if os.environ.get("GITHUB_ACTIONS"):
            print("OK, ANTLR found in classpath")
            # antlrJar = "./antlr-{}-complete.jar".format(ANTLR_VERSION)  # Patch for Github Actions.
            antlrJar = "antlr-{}-complete.jar".format(ANTLR_VERSION)  # Patch for Github Actions.
        else:
            raise OSError("Could not locate ANTLR4 jar in 'CLASSPATH'.")
    else:
        print("OK, ANTLR found in CLASSPATH.")
        for pt in classpath.split(os.pathsep):
            if "antlr" in pt.lower():
                antlrJar = pt
                print(antlrJar)
                break

    if ANTLR_VERSION not in antlrJar:
        raise ValueError("pyA2L requires Antlr {0} -- found '{1}'".format(ANTLR_VERSION, antlrJar))

    if not os.path.exists(antlrJar):
        raise FileNotFoundError("ANTLR4 not found: {0}".format(antlrJar))

    return antlrJar


class AntlrAutogen(Command):
    """Custom command to autogenerate Python code using ANTLR."""

    description = "generate python code using antlr"
    user_options = [
        ("target-dir=", None, "(optional) output directory for antlr artifacts"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Must be snake_case; variable created from user_options.
        # pylint: disable=C0103
        self.target_dir = None

    def finalize_options(self):
        """Post-process options."""
        a2lGrammar = str(ROOT_DIRPATH / "pya2l" / "a2l.g4")
        a2llgGrammar = str(ROOT_DIRPATH / "pya2l" / "a2llg.g4")
        amlGrammar = str(ROOT_DIRPATH / "pya2l" / "aml.g4")
        # distutils.cmd.Command should not have __init__().
        # pylint: disable=W0201
        self.arguments = [a2lGrammar, a2llgGrammar, amlGrammar, "-Dlanguage=Python3"]

        if self.target_dir is not None:
            self.arguments.extend(["-o", self.target_dir])

    def run(self):
        """Run ANTLR."""
        # antlrPath = findAntlr()
        antlrCmd = ["java", "-Xmx500M", "org.antlr.v4.Tool"]
        self.announce(" ".join(antlrCmd + self.arguments))
        subprocess.check_call(antlrCmd + self.arguments)
        clean()


def clean():
    """Remove unneeded files."""
    tokens = ROOT_DIRPATH.joinpath("pya2l").glob("*tokens")
    interp = ROOT_DIRPATH.joinpath("pya2l").glob("*interp")
    listener = (
        list(ROOT_DIRPATH.joinpath("pya2l").glob(i + "Listener.py"))[0]
        for i in ("a2l", "aml")  # No listener for lexer grammars (a2llg.g4).
    )
    for filepath in chain(tokens, interp, listener):
        os.remove(str(filepath))


# pylint: disable=R0901
class CustomBuildPy(setuptools.command.build_py.build_py):
    """Extended build_py which also runs ANTLR."""

    def run(self):
        self.run_command("antlr")
        super().run()


def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {
            "cmd_class": {"antlr": AntlrAutogen, "build_py": CustomBuildPy},
            "zip_safe": False,
        }
    )
