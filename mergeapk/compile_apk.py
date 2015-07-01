#!/usr/bin/python
# coding: UTF-8

import os
import subprocess
import sys

APKTOOL_JAR = "apktool_2.0.0.jar"

def log(str, show=True):
    if (show):
        print(str)

def apk_compile(folder, compileapk):
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, APKTOOL_JAR)
    cmdlist = ["java", "-jar", apktoolfile, "b", folder, "-o", compileapk]
    log("[Logging...] 正在回编译 %s" % compileapk)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] 回编译出错 ...")
        return False
    else:
        log("[Logging...] 回编译完成 ...\n")
        return True