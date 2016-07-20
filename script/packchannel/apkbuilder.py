#!/usr/bin/python
# coding: UTF-8
import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Common
import Log

import subprocess

def apk_compile(folder, compileapk):
    thisdir = os.path.dirname(sys.argv[0])
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "b", folder, "-o", compileapk]
    Log.out("[Logging...] 回编文件名称 : [%s]" % compileapk)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] 回编文件失败")
        return False
    else:
        Log.out("[Logging...] 回编文件成功\n")
        return True

def apk_decompile(apkfile, decompiled_folder=None):
    if (decompiled_folder == None):
        (name, ext) = os.path.splitext(apkfile)
        decompiled_folder = name
    if (not os.path.exists(decompiled_folder)):
        os.makedirs(decompiled_folder)

    #cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-s", "-f" , apkfile, "-o", decompiled_folder]
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-f" , apkfile, "-o", decompiled_folder]
    Log.out("[Logging...] 反编文件名称 : [%s]" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] 反编文件失败")
        return False
    else:
        Log.out("[Logging...] 反编文件成功\n")
        return True

def baksmali(dexfile, outdir):
    cmdlist = [Common.JAVA, "-jar", Common.BAKSMALI_JAR, "-o", outdir, dexfile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] DEX转换失败")
        return False
    else:
        Log.out("[Logging...] DEX转换成功\n")
        return True