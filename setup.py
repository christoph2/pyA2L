# pylint: disable=C0111
import os
import platform
import subprocess
import sys
from itertools import chain
from pathlib import Path

import setuptools.command.build_py
import setuptools.command.develop
from pkg_resources import parse_requirements
from pybind11.setup_helpers import build_ext
from pybind11.setup_helpers import naive_recompile
from pybind11.setup_helpers import ParallelCompile
from pybind11.setup_helpers import Pybind11Extension
from setuptools import Command
from setuptools import find_namespace_packages
from setuptools import setup


def _parse_requirements(filepath):
    with filepath.open() as text_io:
        requirements = list(parse_requirements(text_io))

    return requirements


ROOT_DIRPATH = Path(".")

BASE_REQUIREMENTS = _parse_requirements(ROOT_DIRPATH / "requirements.txt")
TEST_REQUIREMENTS = _parse_requirements(ROOT_DIRPATH / "requirements.test.txt")
ANTLR_VERSION = next(req.specs[0][1] for req in BASE_REQUIREMENTS if req.project_name == "antlr4-python3-runtime")

PB11_INCLUDE_DIRS = subprocess.getoutput("pybind11-config --include")

EXT_NAMES = ["pya2l.preprocessor", "pya2l.a2lparser_ext"]

uname = platform.uname()
if uname.system == "Linux":
    extra_compile_args = ["-fcoroutines"]  # At least required on Raspberry PIs.
else:
    extra_compile_args = []

ext_modules = [
    Pybind11Extension(
        EXT_NAMES[0],
        include_dirs=[PB11_INCLUDE_DIRS, "pya2l/extensions/"],
        sources=["pya2l/preprocessor_wrapper.cpp", "pya2l/extensions/tokenizer.cpp"],
        define_macros=[("EXTENSION_NAME", EXT_NAMES[0])],
        cxx_std=20,
        extra_compile_args=extra_compile_args,
    ),
    Pybind11Extension(
        EXT_NAMES[1],
        include_dirs=[PB11_INCLUDE_DIRS, "pya2l/extensions/"],
        sources=["pya2l/a2lparser_wrapper.cpp", "pya2l/extensions/exceptions.cpp"],
        define_macros=[("EXTENSION_NAME", EXT_NAMES[1])],
        cxx_std=20,
        extra_compile_args=extra_compile_args,
    ),
]


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
        # a2lGrammar = str(ROOT_DIRPATH / "pya2l" / "a2l.g4")
        a2llgGrammar = str(ROOT_DIRPATH / "pya2l" / "a2llg.g4")
        amlGrammar = str(ROOT_DIRPATH / "pya2l" / "aml.g4")
        # distutils.cmd.Command should not have __init__().
        # pylint: disable=W0201
        self.arguments = [a2llgGrammar, amlGrammar, "-Dlanguage=Python3"]

        if self.target_dir is not None:
            self.arguments.extend(["-o", self.target_dir])

    def run(self):
        """Run ANTLR."""
        pwd = Path(os.environ.get("PWD", "."))
        antlrJar = pwd / Path("antlr-{}-complete.jar".format(ANTLR_VERSION))
        if not antlrJar.exists():
            os.system("curl -O -C - -L https://www.antlr.org/download/antlr-{}-complete.jar".format(ANTLR_VERSION))
            # print(f"{antlrJar} not found in '{pwd}'")
            sys.exit(2)
        antlrJar = str(antlrJar)
        antlrCmd = ["java", "-Xmx500M", "-cp", antlrJar, "org.antlr.v4.Tool"]
        self.announce(" ".join(antlrCmd + self.arguments))
        subprocess.check_call(antlrCmd + self.arguments)
        clean()


def clean():
    """Remove unneeded files."""
    # tokens = ROOT_DIRPATH.joinpath("pya2l").glob("*tokens")
    # interp = ROOT_DIRPATH.joinpath("pya2l").glob("*interp")
    # listener = (
    #    list(ROOT_DIRPATH.joinpath("pya2l").glob(i + "Listener.py"))[0]
    #    for i in ("aml")  # No listener for lexer grammars (a2llg.g4).
    # )
    # for filepath in chain(tokens, interp, listener):
    #    os.remove(str(filepath))


# pylint: disable=R0901
class CustomBuildPy(setuptools.command.build_py.build_py):
    """Extended build_py which also runs ANTLR."""

    def run(self):
        self.run_command("antlr")
        super().run()


class CustomDevelop(setuptools.command.develop.develop):
    """Extended develop which also runs ANTLR"""

    def run(self):
        self.run_command("antlr")
        super().run()


with ROOT_DIRPATH.joinpath("pya2l", "version.py").open() as f:
    for line in f:
        if line.startswith("__version__"):
            VERSION = line.split("=")[-1].strip().strip('"')
            break

with ROOT_DIRPATH.joinpath("README.md").open() as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="pya2ldb",
    version=VERSION,
    description="A2L for Python",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Christoph Schueler",
    author_email="cpu12.gems@googlemail.com",
    url="https://www.github.com/Christoph2/pyA2L",
    cmdclass={
        "antlr": AntlrAutogen,
        "build_py": CustomBuildPy,
        "build_ext": build_ext,
        "develop": CustomDevelop,
    },
    ext_modules=ext_modules,
    packages=find_namespace_packages(where=str(ROOT_DIRPATH)),
    package_dir={"pya2l": str(ROOT_DIRPATH / "pya2l")},
    install_requires=list(map(str, BASE_REQUIREMENTS)),
    tests_require=list(map(str, TEST_REQUIREMENTS)),
    package_data={"pya2l.cgen.templates": ["*.tmpl"]},
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    # entry_points={
    #    "console_scripts": [
    #        "a2ldb-imex = pya2l.scripts.a2ldb_imex:main",
    #    ],
    # },
)
