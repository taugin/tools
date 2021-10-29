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

def wait_usb_devices():
    Log.out("\n[Logging...] 等待设备连接")
    try:
        cmd = [Common.ADB, "wait-for-device"]
        devices = []
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
        p.wait()
    except:
        pass
    Log.out("[Logging...] 设备连接成功\n")

def get_select_devices():
    wait_usb_devices()
    try:
        cmd = [Common.ADB, "devices", "-l"]
        devices = []
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
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
        index = input_no("[Logging...] 输入APK序号 : ", 0, apkfilelen)
        if (int(index) == 0):
            return apkFileList
        else:
            apkfile = apkFileList[int(index) - 1]
    elif (apkfilelen == 1):
        apkfile = apkFileList[0]
        Log.out("[Logging...] 顶层APK文件 : [%s]" % apkfile)
    return [apkfile]

def pullspecapk(apkfile, package, to_dir):
    if (apkfile != None and apkfile != ""):
        Log.out("[Logging...] 获取APK文件 : [%s]" % apkfile)
        basename = os.path.basename(apkfile)
        basename, ext = os.path.splitext(basename)
        tempFile = "%s_%ld.apk" % (package, (time.time() * 1000))
        if (to_dir):
            tempDir = os.path.join(os.getcwd(), package)
            if (not os.path.exists(tempDir)):
                os.mkdir(tempDir)
            tempFile = os.path.join(tempDir, tempFile)
        else:
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
        dirpath = os.path.dirname(tempFile)
        newFileName = ""
        apkinfo = get_app_info(tempFile)
        label = None
        vercode = None
        vername = None
        minver = None
        tarver = None
        if (apkinfo != None) :
            label = apkinfo["apklabel"] if "apklabel" in apkinfo else ""
            vercode = apkinfo["vercode"] if "vercode" in apkinfo else ""
            vername = apkinfo["vername"] if "vername" in apkinfo else ""
            minver = apkinfo["min_version"] if "min_version" in apkinfo else ""
            tarver = apkinfo["target_version"] if "target_version" in apkinfo else ""
        if (label != None and len(label) > 0):
            newFileName += label
            if (vercode != None and len(vercode) > 0):
                newFileName += "_"
                newFileName += vercode
            if (vername != None and len(vername) > 0):
                newFileName += "_"
                newFileName += vername
            if (minver != None and len(minver) > 0):
                newFileName += "_"
                newFileName += minver
            if (tarver != None and len(tarver) > 0):
                newFileName += "_"
                newFileName += tarver
        if (basename != "base"):
            newFileName += basename
        newFile = os.path.join(dirpath, newFileName + ".apk")
        if (os.path.exists(newFile)):
            os.remove(newFile)
        Log.out("[Logging...] 获取APK成功 : [%s]" % newFile)
        os.rename(tempFile, newFile)


def parseString(line):
    format_code = ["utf8", "gbk", "gb2312"]
    result = "";
    for f in format_code:
        try:
            result = line.decode(f, "ignore")
            return result
        except:
            pass
    return result

    label = None
    try:
        cmdlist = [Common.AAPT2_BIN, "d", "badging", apkFile]
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

def get_app_info(apkFile):
    '''输出apk的包信息'''
    apk_info = {}
    cmdlist = [Common.AAPT2_BIN, "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)
    apk_info["apkfile"] = apkFile
    tmppkg = ""
    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = parseString(line)
        if (tmp.startswith("package: ")):
            try:
                tmppkg = tmp[len("package: "):]
                tmppkg = tmppkg.replace("\r", "")
                tmppkg = tmppkg.replace("\n", "")
                tmppkg = tmppkg.replace("'", "")
                tmpsplit = tmppkg.split(" ")
                if tmpsplit != None and len(tmpsplit) >= 3:
                    apk_info["pkgname"] = tmpsplit[0].split("=")[1]
                    apk_info["vercode"] = tmpsplit[1].split("=")[1]
                    apk_info["vername"] = tmpsplit[2].split("=")[1]
            except:
                pass
        elif (tmp.startswith("application-label")):
            try:
                tmppkg = tmp
                tmppkg = tmppkg.replace("\r", "")
                tmppkg = tmppkg.replace("\n", "")
                tmppkg = tmppkg.replace("'", "")
                label = tmppkg.split(":")[1]
                apk_info["apklabel"] = label
            except:
                pass
        elif (tmp.startswith("targetSdkVersion")):
            try:
                tmppkg = tmp
                tmppkg = tmppkg.replace("\r", "")
                tmppkg = tmppkg.replace("\n", "")
                tmppkg = tmppkg.replace("'", "")
                target_version = tmppkg.split(":")[1]
                apk_info["target_version"] = target_version
            except:
                pass
        elif (tmp.startswith("sdkVersion")):
            try:
                tmppkg = tmp
                tmppkg = tmppkg.replace("\r", "")
                tmppkg = tmppkg.replace("\n", "")
                tmppkg = tmppkg.replace("'", "")
                min_version = tmppkg.split(":")[1]
                apk_info["min_version"] = min_version
            except:
                pass
    return apk_info

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
        cmdlist = [Common.ADB, "-s", SELECT_DEVICE, "shell", "dumpsys", "package", package]
    else:
        cmdlist = [Common.ADB, "-d", "shell", "dumpsys", "package", package]
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
        if (s.startswith("versionCode=")):
            detail = s[len("versionCode="):]
            if detail != "null":
                Log.out("[Logging...] 显示APK版本 : [%s]" % detail)
        elif (s.startswith("versionName=")):
            detail = s[len("versionName="):]
            if detail != "null":
                Log.out("[Logging...] 显示APK版本 : [%s]" % detail)

def pullapk():
    global SELECT_DEVICE
    SELECT_DEVICE = get_select_devices()
    package = getpackage()
    show_apk_detail(package)
    #sys.exit()
    if (package != None):
        cmd = getCmd()
        if (cmd == "p"):
            apkfiles = getapkfile(package)
            to_dir = len(apkfiles) > 1
            for apkfile in apkfiles:
                pullspecapk(apkfile, package, to_dir)
            time.sleep(3)
        elif (cmd == "u" and confirmUninstall()):
            uninstallApk(package)
            Log.out("[Logging...] 卸载APK成功 : [%s]" % package)
            Common.pause()
    else:
        time.sleep(3)
pullapk()
