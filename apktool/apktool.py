#!/usr/bin/python
# coding: UTF-8
import sys
import os
import subprocess

def log(str, show=True):
    if (show):
        print(str)

def apktool_cmd():
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, "apktool_2.0.3.jar")
    sys.argv[0] = apktoolfile
    cmdlist = ["java", "-jar", apktoolfile]
    cmdlist += sys.argv[1:]
    #log(cmdlist)
    subprocess.call(cmdlist)

apktool_cmd()
