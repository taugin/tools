#!/usr/bin/python
# coding: UTF-8
import sys
import os
# 引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Common
import Log

import re
import subprocess
import time

SELECT_DEVICE = None

def input_no(start, end):
    while True:
        i = input("请输入设备顺序 : ")
        if i != None and i.isdigit() and int(i) >= start and int(i) <= end:
            return i
    return 1

def get_select_devices():
    try:
        cmd = [Common.ADB, "devices", "-l"]
        devices = []
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        p.wait(5)
        allLines = p.stdout.readlines()
        for s in allLines:
            s = str(s, "utf-8")
            s = s.replace("\r", "")
            s = s.replace("\n", "")
            if (s.startswith("List") or len(s) == 0):
                continue
            devices.append([re.split("\s+", s)[0], s])
        if (len(devices) > 1):
            Log.out("发现的设备列表")
            for index in range(0, len(devices)):
                Log.out("%s : %s" % (index + 1, devices[index][1]))
            no = input_no(1, len(devices))
            return devices[int(no) - 1][0]
        elif(len(devices) == 1):
            return devices[0][0]
    except:
        pass
    return None

def getpackage():
    if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
        cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "shell", "dumpsys", "activity", "top"]
    else:
        cmdlist = [Common.ADB, "-d", "shell", "dumpsys", "activity", "top"]
    p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    # p.wait()
    pkglist = []
    if (p != None):
        for line in p.stdout.readlines():
            string = line.decode().replace("\n", "")
            string = string.lstrip()
            if (string.startswith("ACTIVITY")):
                str_list = string.split(" ")
                if (str_list != None and len(str_list) > 1):
                    str_list = str_list[1].split("/")
                    if (str_list != None and len(str_list) > 0):
                        pkglist += [str_list[0]]
    package = pkglist[-1] if len(pkglist) > 0 else "Can not find top package"
    Log.out("[Logging...] 顶层APK包名 : [%s]" % package)
    return package

def getapkfile(package):
    if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
        cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "shell", "pm", "path", package]
    else:
        cmdlist = [Common.ADB, "-d", "shell", "pm", "path", package]
    p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    apkfile = None
    if (p != None):
        for line in p.stdout.readlines():
            string = line.decode().replace("\n", "")
            tmp = string.strip()
            if (tmp.startswith("package:")):
                tmp = tmp[len("package:"):]
                if (tmp != None and len(tmp) > 1):
                    Log.out("[Logging...] 顶层APK文件 : [%s]" % tmp)
                    apkfile = tmp
    return apkfile

def pullspecapk(apkfile, package):
    if (apkfile != None and apkfile != ""):
        Log.out("[Logging...] 正在获取APK")
        tempFile = "%s_%ld.apk" % (package, (time.time() * 1000))
        tempFile = os.path.join(os.getcwd(), tempFile)
        tempFile = os.path.normpath(tempFile)
        f = open(tempFile, "wb")
        f.close()
        if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
            cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "pull", apkfile, tempFile]
        else:
            cmdlist = [Common.ADB, "-d", "pull", apkfile, tempFile]
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
    label = None
    try:
        cmdlist = [Common.AAPT_BIN, "d", "badging", apkFile]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
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
    except:
        pass
    return label

def pullapk():
    global SELECT_DEVICE
    SELECT_DEVICE = get_select_devices()
    package = getpackage()
    if (package != None):
        apkfile = getapkfile(package)
        pullspecapk(apkfile, package)

pullapk()
