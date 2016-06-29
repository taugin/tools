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

import os
import subprocess


def getpackage():
    cmdlist = [Common.ADB, "shell", "dumpsys", "activity", "top"]
    p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    #p.wait()
    package = None
    if (p != None):
        for line in p.stdout.readlines():
            string = line.decode().replace("\n", "")
            string = string.lstrip()
            if (string.startswith("ACTIVITY")):
                list = string.split(" ")
                if (list != None and len(list) > 1):
                    list = list[1].split("/")
                    if (list != None and len(list) > 0):
                        package = list[0]
                        Log.out("[Logging...] 顶层APK包名 : [%s]" % package)
    return package

def getapkfile(package):
    cmdlist = [Common.ADB, "shell", "pm", "list", "packages", "-f", package]
    p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    apkfile = None
    if (p != None):
        for line in p.stdout.readlines():
            string = line.decode().replace("\n", "")
            string = string.strip()
            if (string.startswith("package:")):
                tmp = string[len("package:"):]
                tmp = tmp.split("=")
                if (tmp != None and len(tmp) > 1):
                    if (tmp[1] == package):
                        Log.out("[Logging...] 顶层APK文件 : [%s]" % tmp[0])
                        apkfile = tmp[0]
    return apkfile

def pullspecapk(apkfile):
    if (apkfile != None and apkfile != ""):
        Log.out("[Logging...] 正在获取APK")
        cmdlist = [Common.ADB, "pull", apkfile]
        subprocess.call(cmdlist)

def pullapk():
    package = getpackage()
    if (package != None):
        apkfile = getapkfile(package)
        pullspecapk(apkfile)

pullapk()