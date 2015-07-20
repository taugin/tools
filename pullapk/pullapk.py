#!/usr/bin/python
# coding: UTF-8
import sys
import os
import subprocess

def log(str, show=True):
    if (show):
        print(str)

def getpackage():
    cmdlist = ["adb", "shell", "dumpsys", "activity", "top"]
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
                        log("[Logging...] 顶层APK包名 : [%s]" % package)
    return package

def getapkfile(package):
    cmdlist = ["adb", "shell", "pm", "list", "packages", "-f", package]
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
                        log("[Logging...] 顶层APK文件 : [%s]" % tmp[0])
                        apkfile = tmp[0]
    return apkfile

def pullspecapk(apkfile):
    if (apkfile != None and apkfile != ""):
        log("[Logging...] 正在获取APK")
        cmdlist = ["adb", "pull", apkfile]
        subprocess.call(cmdlist)

def pullapk():
    package = getpackage()
    apkfile = getapkfile(package)
    pullspecapk(apkfile)

pullapk()