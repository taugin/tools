#!/usr/bin/python
# coding: UTF-8
import sys
import os

import Common
import Log
import Utils
import random
import subprocess

def apk_compile(folder, compileapk):
    thisdir = os.path.dirname(sys.argv[0])
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "b", folder, "-o", compileapk]
    Log.out("[Logging...] 回编文件名称 : [%s]" % compileapk)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 回编文件失败")
        return False
    else:
        Log.out("[Logging...] 回编文件成功\n")
        return True

def apk_decompile(apkfile, decompiled_folder=None):
    if (decompiled_folder == None):
        (name, ext) = os.path.splitext(apkfile)
        decompiled_folder = name

    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-f" , apkfile, "-o", decompiled_folder]
    Log.out("[Logging...] 反编文件名称 : [%s]" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 反编文件失败")
        return False
    else:
        Log.out("[Logging...] 反编文件成功\n")
        return True

#apk对齐
def alignapk(unalignapk, finalapk):
    finalapk = os.path.normpath(finalapk)
    Log.out("[Logging...] 正在对齐文件 : [%s]" % finalapk, True)
    cmdlist = [Common.ZIPALIGN, "-f", "4", unalignapk, finalapk]
    subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 文件对齐成功\n")
    return True