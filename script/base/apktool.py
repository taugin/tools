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
    ret = subprocess.call(cmdlist)
    if (ret == 0) :
        return True
    else:
        return False

def signapk(srcapk, dstapk):
    Log.out("")
    cmdlist = ["python", SIGNAPK_FILE, "-o", dstapk, srcapk]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

#apk对齐
def alignapk(unalignapk, finalapk):
    finalapk = os.path.normpath(finalapk)
    Log.out("[Logging...] 正在对齐文件 : [%s]" % finalapk, True)
    cmdlist = [Common.ZIPALIGN, "-f", "4", unalignapk, finalapk]
    subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 文件对齐成功\n")
    return True

ret = apktool_cmd()

#回编译签名
if (ret and len(sys.argv) > 1 and sys.argv[1] == "b"):
    srcapk = None
    signedapk = None
    alignedapk = None;
    opts, args = getopt.getopt(sys.argv[3:], "o:")
    for op, value in opts:
        if (op == "-o"):
            srcapk = value
    if (srcapk != None and len(srcapk) > 0) :
        (tmpname, ext) = os.path.splitext(srcapk)
        signedapk = tmpname + "-signed.apk"
        alignedapk = tmpname + "-final.apk"
        if (signapk(srcapk, signedapk) == True):
            if (os.path.exists(srcapk)):
                os.remove(srcapk)
            if (alignapk(signedapk, alignedapk) == True):
                if (os.path.exists(signedapk)):
                    os.remove(signedapk)

Common.pause()