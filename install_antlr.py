#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform as pf
from os import environ
from subprocess import check_call

print(environ)

VERSION = "4.9.3"
ANTLR = "https://www.antlr.org/download/antlr-{}-complete.jar".format(VERSION)


os = pf.system().lower()
uname = pf.uname()
print(uname)


def main():
    if os == "windows":
        check_call(["Invoke-WebRequest", "-O", "-C", "-", "-L", ANTLR])
        check_call(["choco", "install", "adoptopenjdk"])
    else:
        check_call(["curl", "-O", "-C", "-", "-L", ANTLR])
        # check_call(["sudo", "apt-get", "install", "-y", "adoptopenjdk"])
        check_call(["yum", "install", "adoptopenjdk"])


if __name__ == "__main__":
    main()
