#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform as pf
from os import environ
from subprocess import check_call

environ["FLONZ"] = "buhh"

VERSION = "4.9.3"
ANTLR = "https://www.antlr.org/download/antlr-{}-complete.jar".format(VERSION)


os = pf.system().lower()
uname = pf.uname()
print(uname)


def main():
    if os == "windows":
        check_call(["Invoke-WebRequest", "-O", "-C", "-", "-L", ANTLR])
    else:
        # elif os == "linux":
        check_call(["curl", "-O", "-C", "-", "-L", ANTLR])


if __name__ == "__main__":
    main()
