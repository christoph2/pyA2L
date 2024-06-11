#!/usr/bin/env python

import multiprocessing as mp
import os
import re
import subprocess  # nosec
import sys
from pathlib import Path

from pkg_resources import parse_requirements
from setuptools import Distribution, Extension

from pybind11.setup_helpers import build_ext


GIT_TAG_RE = re.compile(r"refs/tags/v?(\d\.\d{1,3}.\d{1,3})")


def sort_by_version(version: str) -> tuple[int]:
    h, m, s = version.split(".")
    return int(h), int(m), int(s)


def fetch_tags(repo: str) -> list[str]:
    res = subprocess.run(["git", "ls-remote", "--tags", repo], shell=False, capture_output=True, text=True)  # nosec
    if res.returncode == 0:
        return []
    tag_set = set()
    for tag in res.stdout.splitlines():
        ma = GIT_TAG_RE.search(tag)
        if ma:
            tag_set.add(ma.group(1))
    return sorted(tag_set, key=sort_by_version)


def most_recent_tag(repo: str) -> str | None:
    tags = fetch_tags(repo)
    return tags[-1] if tags else None


EXT_NAMES = ["pya2l.preprocessor", "pya2l.a2lparser_ext"]


def _parse_requirements(filepath):
    print("FP:", filepath, filepath.absolute())
    with filepath.open() as text_io:
        requirements = list(parse_requirements(text_io))

    return requirements


#################################################################
#################################################################
#################################################################

# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}


# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())
        print("CMakeExtension()")


class CMakeBuild(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        print("CMakeBuild::build_extension()")
        # Must be in this form due to bug in .resolve() only fixed in Python 3.10+

        # ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        # extdir = ext_fullpath.parent.resolve()

        # Using this requires trailing slash for auto-detection & inclusion of
        # auxiliary "native" libs

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        # CMake lets you override the generator - we need to check this.
        # Can be set with Conda-Build, for example.
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")

        # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
        # EXAMPLE_VERSION_INFO shows you how to pass a value into the C++ code
        # from Python.
        cmake_args = [
            # f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
        ]
        build_args = []
        # Adding CMake arguments set as environment variable
        # (needed e.g. to build for ARM OSx on conda-forge)
        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        # In this example, we pass in the version to C++. You might not need to.
        # cmake_args += [f"-DEXAMPLE_VERSION_INFO={self.distribution.get_version()}"]

        if self.compiler.compiler_type != "msvc":
            # Using Ninja-build since it a) is available as a wheel and b)
            # multithreads automatically. MSVC would require all variables be
            # exported for Ninja to pick it up, which is a little tricky to do.
            # Users can override the generator with CMAKE_GENERATOR in CMake
            # 3.15+.
            if not cmake_generator or cmake_generator == "Ninja":
                try:
                    import ninja

                    ninja_executable_path = Path(ninja.BIN_DIR) / "ninja"
                    cmake_args += [
                        "-GNinja",
                        f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                    ]
                except ImportError:
                    pass

        else:
            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

            # Multi-config generators have a different way to specify configs
            if not single_config:
                # cmake_args += [
                #    f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
                # ]
                build_args += ["--config", cfg]

        if sys.platform.startswith("darwin"):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += [f"-j{self.parallel}"]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)

        print("Running CMake:", cmake_args)
        subprocess.run(["cmake", ext.sourcedir, *cmake_args], cwd=build_temp, check=True)  # nosec

        cmake_args += [f"--parallel {mp.cpu_count()}"]

        subprocess.run(["cmake", "--build", ".", *build_args], cwd=build_temp, check=True)  # nosec

        subprocess.run(["cmake", "--install", "."], cwd=build_temp, check=True)  # nosec


def invoke_command(distribution: Distribution, name: str) -> None:
    cmd = distribution.cmdclass.get(name)(distribution)
    print(f"Building target {name!r}...")
    cmd.inplace = 1
    cmd.ensure_finalized()
    cmd.run()


###

if __name__ == "__main__":
    distribution = Distribution(
        {
            "cmdclass": {
                "build_ext": CMakeBuild,
            },
            "name": "pya2ldb",
            "ext_modules": [CMakeExtension("pya2l.preprocessor")],
            # "package_dir": {"pya2ldb": str(ROOT_DIRPATH / "pya2ldb")},
        }
    )
    invoke_command(distribution, "build_ext")
