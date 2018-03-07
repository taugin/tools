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
import getopt
import Log
import subprocess

SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "signapk.py")

def apktool_cmd():
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR]
    cmdlist += sys.argv[1:]
    subprocess.call(cmdlist)

def signapk(dstapk):
    Log.out("")
    cmdlist = ["python", SIGNAPK_FILE, dstapk]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

apktool_cmd()

#回编译签名
if (len(sys.argv) > 1 and sys.argv[1] == "b"):
    apkfile = None
    opts, args = getopt.getopt(sys.argv[3:], "o:")
    for op, value in opts:
        if (op == "-o"):
            apkfile = value
    if (apkfile != None and len(apkfile) > 0) :
        if (signapk(apkfile) == True):
            if (os.path.exists(apkfile)):
                os.remove(apkfile)

Common.pause()