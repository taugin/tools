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
INSTALL_FILE = os.path.join(os.path.dirname(sys.argv[0]), "sf.py")

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

def getApkInfo(apkFile):
    pkgname = ""
    vercode = ""
    vername = ""
    apklabel = ""
    targetSdkVersion = ""
    minSdkVersion = ""
    try:
        cmdlist = [Common.AAPT2_BIN, "d", "badging", apkFile]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
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
                        pkgname = tmpsplit[0].split("=")[1]
                        vercode = tmpsplit[1].split("=")[1]
                        vername = tmpsplit[2].split("=")[1]
                except:
                    pass
            elif (tmp.startswith("application-label")):
                try:
                    tmppkg = tmp
                    tmppkg = tmppkg.replace("\r", "")
                    tmppkg = tmppkg.replace("\n", "")
                    tmppkg = tmppkg.replace("'", "")
                    label = tmppkg.split(":")[1]
                    apklabel = label
                except:
                    pass
            elif (tmp.startswith("targetSdkVersion")):
                try:
                    tmppkg = tmp
                    tmppkg = tmppkg.replace("\r", "")
                    tmppkg = tmppkg.replace("\n", "")
                    tmppkg = tmppkg.replace("'", "")
                    label = tmppkg.split(":")[1]
                    targetSdkVersion = label
                except:
                    pass
            elif (tmp.startswith("sdkVersion")):
                try:
                    tmppkg = tmp
                    tmppkg = tmppkg.replace("\r", "")
                    tmppkg = tmppkg.replace("\n", "")
                    tmppkg = tmppkg.replace("'", "")
                    label = tmppkg.split(":")[1]
                    minSdkVersion = label
                except:
                    pass
    except:
        pass
    return pkgname, vercode, vername, apklabel, targetSdkVersion, minSdkVersion

def apktool_cmd():
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR]
    cmdlist += sys.argv[1:]
    cmdlist += ["--only-main-classes"]
    showlist = []
    for cmd in cmdlist:
        showlist += [os.path.basename(cmd)]
    Log.out("[Logging...] 执行命令详情 : [%s]\n" % " ".join(showlist))
    Log.out("[Logging...] 显示详情")
    ret = subprocess.call(cmdlist)
    Log.out("[Logging...] 编译完成")
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
    if (False):
        Log.out("[Logging...] 正在对齐文件 : [%s]" % finalapk, True)
        cmdlist = [Common.ZIPALIGN, "-f", "4", unalignapk, finalapk]
        subprocess.call(cmdlist, stdout=subprocess.PIPE)
        Log.out("[Logging...] 文件对齐成功\n")
    else:
        os.rename(unalignapk, finalapk)
    return True

def needInstall():
    result = input("[Logging...] 是否需要安装 (Y/N) ")
    if result == "Y" or result == "y":
        return True
    return False

def installApk(finalapk):
    Log.out("")
    cmdlist = ["python", INSTALL_FILE, "-i", finalapk]
    subprocess.call(cmdlist)

def showApkInfo(apkFile):
    Log.out("")
    pkgname, vercode, vername, apklabel, targetSdkVersion, minSdkVersion = getApkInfo(srcapk)
    output = " 应用路径 : [%s] " % srcapk
    Log.out("[Logging...]%s" %output)
    output = " 应用名称 : [%s] " % apklabel
    Log.out("[Logging...]%s" %output)
    output = " 应用包名 : [%s] " % pkgname
    Log.out("[Logging...]%s" %output)
    output = " 应用版本 : [%s] " % vercode
    Log.out("[Logging...]%s" %output)
    output = " 应用版本 : [%s] " % vername
    Log.out("[Logging...]%s" %output)
    output = " 最小版本 : [%s] " % minSdkVersion
    Log.out("[Logging...]%s" %output)
    output = " 目标版本 : [%s] " % targetSdkVersion
    Log.out("[Logging...]%s" %output)
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
    showApkInfo(srcapk)
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
    if (needInstall()):
        installApk(alignedapk)
else:
    Common.pause()