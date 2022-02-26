#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform as pf
from os import environ
from subprocess import check_call


VERSION = "4.9.3"
ANTLR = "https://www.antlr.org/download/antlr-{}-complete.jar".format(VERSION)


print("MY-ENVIRON:", environ)
os = pf.system().lower()
uname = pf.uname()
print("MY-UNAME:", uname)


def main():
    if os == "windows":
        # check_call(["Invoke-WebRequest", "-O", "-C", "-", "-L", ANTLR])
        check_call(["choco", "install", "adoptopenjdk-16-hotspot"])
        check_call(["curl", "-O", "-C", "-", "-L", ANTLR])
    else:
        check_call(["curl", "-O", "-C", "-", "-L", ANTLR])
        # check_call(["sudo", "apt-get", "install", "-y", "adoptopenjdk"])
        check_call(
            """sudo cat << 'EOF' >/etc/yum.repos.d/adoptopenjdk.repo
[AdoptOpenJDK]
name=AdoptOpenJDK
baseutl=http://adoptopenjdk.jfrog.io/artifactory/rpm/centos/$releasever/$basearch
enabled=1
gpgcheck=1
gpgkey=http://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public
EOF""",
            shell=True,
        )
        check_call(["sudo", "yum", "install", "adoptopenjdk-16-hotspot"])


if __name__ == "__main__":
    main()
