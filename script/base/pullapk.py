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
import time


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
                str_list = string.split(" ")
                if (str_list != None and len(str_list) > 1):
                    str_list = str_list[1].split("/")
                    if (str_list != None and len(str_list) > 0):
                        package = str_list[0]
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

def pullspecapk(apkfile, package):
    if (apkfile != None and apkfile != ""):
        Log.out("[Logging...] 正在获取APK")
        tempFile = "tmp_file_%ld.apk" % (time.time() * 1000)
        tempFile = os.path.join(os.getcwd(), tempFile)
        tempFile = os.path.normpath(tempFile)
        f = open(tempFile, "wb")
        f.close()
        cmdlist = [Common.ADB, "pull", apkfile, tempFile]
        subprocess.call(cmdlist)
        if not os.path.exists(tempFile):
            return
        label = getlabel(tempFile)
        if (label == None or len(label) <= 0):
            label = package
        dirpath = os.path.dirname(tempFile)
        newFile = os.path.join(dirpath, label + ".apk")
        if (os.path.exists(newFile)):
            os.remove(newFile)
        Log.out("[Logging...] 获取APK成功 : [%s]" % newFile)
        os.rename(tempFile, newFile)

def getlabel(apkFile):
    cmdlist = [Common.AAPT_BIN, "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)

    tmppkg = ""
    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = str(line, "utf-8")
        if (tmp.startswith("application-label")):
            tmppkg = tmp
            break;
    tmppkg = tmppkg.replace("\r", "")
    tmppkg = tmppkg.replace("\n", "")
    tmppkg = tmppkg.replace("'", "")
    label = tmppkg.split(":")[1]
    return label

def pullapk():
    package = getpackage()
    if (package != None):
        apkfile = getapkfile(package)
        pullspecapk(apkfile, package)

pullapk()