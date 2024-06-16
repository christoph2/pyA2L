#!/usr/bin/env python

import multiprocessing as mp
import os
import platform
import re
import subprocess  # nosec
import sys
from pathlib import Path

# from pprint import pprint
from tempfile import TemporaryDirectory


print("Platform", platform.system())

TOP_DIR = Path(__file__).parent

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


def banner(msg: str) -> None:
    print("=" * 80)
    print(str.center(msg, 80))
    print("=" * 80)


def build_extension(debug: bool = False) -> None:
    print("CMakeBuild::build_extension()")

    debug = int(os.environ.get("DEBUG", 0)) or debug
    cfg = "Debug" if debug else "Release"

    # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
    # EXAMPLE_VERSION_INFO shows you how to pass a value into the C++ code
    # from Python.
    cmake_args = [
        # f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
        # "-G Ninja",
        f"-DPYTHON_EXECUTABLE={sys.executable}",
        f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
    ]
    build_args = ["--config Release", "--verbose"]
    # Adding CMake arguments set as environment variable
    # (needed e.g. to build for ARM OSx on conda-forge)

    if sys.platform.startswith("darwin"):
        # Cross-compile support for macOS - respect ARCHFLAGS if set
        archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
        if archs:
            cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

    build_temp = Path(TemporaryDirectory(suffix=".build-temp").name) / "extension_it_in"
    # build_temp = Path(".") / "build"
    print("cwd:", os.getcwd(), "build-dir:", build_temp, "top:", str(TOP_DIR))
    # print("PHILEZ:", os.listdir(TOP_DIR))
    if not build_temp.exists():
        build_temp.mkdir(parents=True)

    banner("Step #1: Configure")
    # cmake_args += ["--debug-output"]
    print("aufruf:", ["cmake", str(TOP_DIR), *cmake_args])
    subprocess.run(["cmake", str(TOP_DIR), *cmake_args], cwd=build_temp, check=True)  # nosec

    cmake_args += [f"--parallel {mp.cpu_count()}"]

    banner("Step #2: Build")
    # subprocess.run(["cmake", "--build", ".", *build_args], cwd=build_temp, check=True)  # nosec
    # build_args += ["-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
    subprocess.run(["cmake", "--build", build_temp, *build_args], cwd=TOP_DIR, check=True)  # nosec

    banner("Step #3: Install")
    # subprocess.run(["cmake", "--install", "."], cwd=build_temp, check=True)  # nosec
    subprocess.run(["cmake", "--install", build_temp], cwd=TOP_DIR, check=True)  # nosec


if __name__ == "__main__":
    cm = Path("CMakeLists.txt").exists()
    print("CMakeLists.txt vorhanden?", cm)
    if cm:
        build_extension()
