#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform as pf
from os import environ
from subprocess import call
from subprocess import check_call


VERSION = "4.9.3"
ANTLR = "https://www.antlr.org/download/antlr-{}-complete.jar".format(VERSION)


print("MY-ENVIRON:", environ)
os = pf.system().lower()
uname = pf.uname()
print("MY-UNAME:", uname)


def main():
    if os == "windows":
        call(["choco", "install", "adoptopenjdk"])
        call(["curl", "-O", "-C", "-", "-L", ANTLR])
        call(["dir"])
    else:
        call(["curl", "-O", "-C", "-", "-L", ANTLR])
        call(
            """cat << 'EOF' >/etc/yum.repos.d/adoptopenjdk.repo
[AdoptOpenJDK]
name=AdoptOpenJDK
baseutl=http://adoptopenjdk.jfrog.io/artifactory/rpm/centos/$releasever/$basearch
enabled=1
gpgcheck=1
gpgkey=http://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public
EOF""",
            shell=True,
        )
        # call(["yum", "install", "adoptopenjdk-16-hotspot"])
        call(["yum", "update"])
        call(["yum", "install", "adoptopenjdk"])
        call(["ls", "-l", "-A"])


if __name__ == "__main__":
    main()
