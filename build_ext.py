#!/usr/bin/env python

import multiprocessing as mp
import os
import platform
import re
import subprocess  # nosec
import sys
import sysconfig
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional


TOP_DIR = Path(__file__).parent

GIT_TAG_RE = re.compile(r"refs/tags/v?(\d\.\d{1,3}.\d{1,3})")

print("Platform", platform.system())
uname = platform.uname()
if uname.system == "Darwin":
    os.environ["MACOSX_DEPLOYMENT_TARGET"] = "11.0"

VARS = sysconfig.get_config_vars()

def get_python_base() -> str:
    # Applies in this form only to Windows.
    if "base" in VARS and VARS["base"]:
        return VARS["base"]
    if "installed_base" in VARS and VARS["installed_base"]:
        return VARS["installed_base"]


def alternate_libdir(pth: str):
    base = Path(pth).parent
    libdir = Path(base) / "libs"
    if libdir.exists():
        # available_libs = os.listdir(libdir)
        return str(libdir)
    else:
        return ""


def get_py_config() -> dict:
    pynd = VARS["py_version_nodot"]  # Should always be present.
    include = sysconfig.get_path("include")  # Seems to be cross-platform.
    if uname.system == "Windows":
    #library = f"python{pynd}.lib"
        base = get_python_base()
        libdir = Path(base) / "libs"
        if libdir.exists():
            available_libs = os.listdir(libdir)
            if library in available_libs:
                libdir = str(libdir)
            else:
                libdir = ""
        else:
            libdir = alternate_libdir(include)
    else:
        libdir = VARS["LIBDIR"]
        library = VARS["LDLIBRARY"]
        if not (Path(libdir) / library).exists():
            #arch = VARS["MULTIARCH"]
            arch_dir = VARS["multiarchsubdir"]
            if arch_dir.startswith("/"):
                arch_dir = arch_dir[1:]
                if (Path(libdir) / Path(arch_dir) / library).exists():
                    xd = Path(libdir) / Path(arch_dir) / library
                    libdir = str(Path(libdir) / Path(arch_dir))
                else:
                    print("Could NOT locate Python link-library!!!")                                    
    print("LIB-DIR:", libdir, library)
    return dict(exe=sys.executable, include=include, libdir=libdir, library=library)


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


def most_recent_tag(repo: str) -> Optional[str]:  # noqa: UP007
    tags = fetch_tags(repo)
    return tags[-1] if tags else None


def banner(msg: str) -> None:
    print("=" * 80)
    print(str.center(msg, 80))
    print("=" * 80)


# tool["cs_build"]={"antlr4_version": "4.13.0"}


def build_extension(debug: bool = False, use_temp_dir=True) -> None:
    print("CMakeBuild::build_extension()")

    debug = int(os.environ.get("DEBUG", 0)) or debug
    cfg = "Debug" if debug else "Release"

    py_cfg = get_py_config()

    cmake_args = [
        f"-DPython3_EXECUTABLE={py_cfg['exe']}",
        f"-DPython3_INCLUDE_DIR={py_cfg['include']}",
        f"-DPython3_LIBRARY={str(Path(py_cfg['libdir']) / Path(py_cfg['library']))}",  # noqa: RUF010
        f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
    ]

    build_args = ["--config Release", "--verbose"]
    # Adding CMake arguments set as environment variable
    # (needed e.g. to build for ARM OSx on conda-forge)

    # cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 /path/to/src

    if sys.platform.startswith("darwin"):
        # Cross-compile support for macOS - respect ARCHFLAGS if set
        archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
        if archs:
            cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

    if use_temp_dir:
        build_temp = Path(TemporaryDirectory(suffix=".build-temp").name) / "extension_it_in"
    else:
        build_temp = Path(os.getcwd()) / "build"

    print("cwd:", os.getcwd(), "build-dir:", build_temp, "top:", str(TOP_DIR))

    if not build_temp.exists():
        build_temp.mkdir(parents=True)

    banner("Step #1: Configure")
    # cmake_args += ["--debug-output"]
    subprocess.run(["cmake", "-S", str(TOP_DIR), *cmake_args], cwd=build_temp, check=True)  # nosec

    cmake_args += [f"--parallel {mp.cpu_count()}"]

    banner("Step #2: Build")
    # subprocess.run(["cmake", "--build", ".", *build_args], cwd=build_temp, check=True)  # nosec
    # build_args += ["-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
    subprocess.run(["cmake", "--build", build_temp, *build_args], cwd=TOP_DIR, check=True)  # nosec

    banner("Step #3: Install")
    # subprocess.run(["cmake", "--install", "."], cwd=build_temp, check=True)  # nosec
    subprocess.run(["cmake", "--install", build_temp], cwd=TOP_DIR, check=True)  # nosec


if __name__ == "__main__":
    includes = subprocess.getoutput("pybind11-config --cmakedir")  # nosec
    os.environ["pybind11_DIR"] = includes
    build_extension(use_temp_dir=True)
