#!/usr/bin/python
# coding: UTF-8

import os
import subprocess
import sys

APKTOOL_JAR = "apktool_2.0.0.jar"

def log(str, show=True):
    if (show):
        print(str)

def apk_decompile(apkfile, decompiled_folder=None):
    if (decompiled_folder == None):
        (name, ext) = os.path.splitext(apkfile)
        decompiled_folder = name

    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, APKTOOL_JAR)
    cmdlist = ["java", "-jar", apktoolfile, "d", "-s", "-f" , apkfile, "-o", decompiled_folder]
    log("[Logging...] 正在反编译 %s" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] 反编译出错 ...")
        return False
    else:
        log("[Logging...] 反编译完成 ...\n")
        return True