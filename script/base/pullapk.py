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

def input_no(prompt, start, end):
    try:
        while True:
            i = input(prompt)
            if i != None and i.isdigit() and int(i) >= start and int(i) <= end:
                return i
    except:
        Log.out("")
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
        if (len(devices) > 0):
            Log.out("发现的设备列表 : ")
            for index in range(0, len(devices)):
                Log.out("%s : %s" % (index + 1, devices[index][1]))
            no = 1
            if (len(devices) > 1):
                no = input_no("请输入设备顺序 : ", 1, len(devices))
            else:
                Log.out("")
            return devices[int(no) - 1][0]
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
    actlist = []
    if (p != None):
        for line in p.stdout.readlines():
            string = line.decode().replace("\n", "")
            string = string.lstrip()
            if (string.startswith("ACTIVITY")):
                str_list = string.split(" ")
                if (str_list != None and len(str_list) > 1):
                    str_list = str_list[1].split("/")
                    if (str_list != None and len(str_list) > 1):
                        pkglist += [str_list[0]]
                        actlist += [str_list[1]]
    package = pkglist[-1] if len(pkglist) > 0 else None
    activity = actlist[-1] if len(actlist) > 0 else None
    Log.out("[Logging...] 顶层APK包名 : [%s]" % (package if package != None else "Can not find top package"))
    Log.out("[Logging...] 顶层APK类名 : [%s]" % (activity if activity != None else "Can not find top activity"))
    return package

def getapkfile(package):
    if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
        cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "shell", "pm", "path", package]
    else:
        cmdlist = [Common.ADB, "-d", "shell", "pm", "path", package]
    p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    apkFileList = []
    apkfile = None
    if (p != None):
        for line in p.stdout.readlines():
            string = line.decode().replace("\n", "")
            tmp = string.strip()
            if (tmp.startswith("package:")):
                tmp = tmp[len("package:"):]
                if (tmp != None and len(tmp) > 1):
                    apkFileList += [tmp]

    apkfilelen = len(apkFileList)
    Log.out("[Logging...] 顶层APK数量 : [%d]" % apkfilelen)
    if (apkfilelen > 1):
        number = 1
        for apk in apkFileList:
            Log.out("[Logging...] 顶层APK文件 : [%d] [%s]" % (number, apk))
            number = number + 1
        index = input_no("[Logging...] 输入APK序号 : ", 1, apkfilelen)
        apkfile = apkFileList[int(index) - 1]
    elif (apkfilelen == 1):
        apkfile = apkFileList[0]
        Log.out("[Logging...] 顶层APK文件 : [%s]" % apkfile)
    return apkfile

def pullspecapk(apkfile, package):
    if (apkfile != None and apkfile != ""):
        Log.out("[Logging...] 获取APK文件 : [%s]" % apkfile)
        tempFile = "%s_%ld.apk" % (package, (time.time() * 1000))
        tempFile = os.path.join(os.getcwd(), tempFile)
        tempFile = os.path.normpath(tempFile)
        f = open(tempFile, "wb")
        f.close()
        if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
            cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "pull", apkfile, tempFile]
        else:
            cmdlist = [Common.ADB, "-d", "pull", apkfile, tempFile]
        subprocess.call(cmdlist, stdout=subprocess.PIPE)
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

def uninstallApk(package):
    if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
        cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "uninstall", package]
    else:
        cmdlist = [Common.ADB, "-d", "uninstall", package]
    subprocess.Popen(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

def confirmUninstall():
    result = input("[Logging...] 确认卸载APK : [Y/N] ")
    if result == "Y" or result == "y":
        return True
    return False

def getCmd():
    result = input("[Logging...] 处理APK文件 : [拉取 : P , 卸载 : U] ")
    if (result == None) :
        return None
    result = result.lower()
    return result

def show_apk_detail(package):
    if (package == None or len(package) <= 0):
        return
    if (SELECT_DEVICE != None and len(SELECT_DEVICE) > 0) :
        cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "shell", "pm", "query-activities", package]
    else:
        cmdlist = [Common.ADB, "-d", "shell", "pm", "query-activities", package]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    tmppkg = ""
    tmp = ""
    str_list = []
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = str(line, "utf-8")
        tmp = tmp.replace("\r", "")
        tmp = tmp.replace("\n", "")
        tmp = tmp.strip()
        tmpsplit = tmp.split(" ")
        str_list += tmpsplit

    for s in str_list:
        detail = None
        if s.startswith("nonLocalizedLabel="):
            detail = s[len("nonLocalizedLabel="):]
            if detail == "null":
                detail = None
            else:
                detail = s
        elif (s.startswith("sourceDir=")):
            detail = s[len("sourceDir="):]
            if detail == "null":
                detail = None
            else:
                detail = s
        elif (s.startswith("minSdkVersion=")):
            detail = s[len("minSdkVersion="):]
            if detail == "null":
                detail = None
            else:
                detail = s
        elif (s.startswith("targetSdkVersion=")):
            detail = s[len("targetSdkVersion="):]
            if detail == "null":
                detail = None
            else:
                detail = s
        elif (s.startswith("versionCode=")):
            detail = s[len("versionCode="):]
            if detail == "null":
                detail = None
            else:
                detail = s
        elif (s.startswith("dataDir=")):
            detail = s[len("dataDir="):]
            if detail == "null":
                detail = None
            else:
                detail = s
        if detail != None:
            Log.out("[Logging...] 显示APK详情 : [%s]" % detail)
def pullapk():
    global SELECT_DEVICE
    SELECT_DEVICE = get_select_devices()
    package = getpackage()
    show_apk_detail(package)
    #sys.exit()
    if (package != None):
        cmd = getCmd()
        if (cmd == "p"):
            apkfile = getapkfile(package)
            pullspecapk(apkfile, package)
            time.sleep(3)
        elif (cmd == "u" and confirmUninstall()):
            uninstallApk(package)
            Log.out("[Logging...] 卸载APK成功 : [%s]" % package)
            Common.pause()
    else:
        time.sleep(3)
pullapk()
