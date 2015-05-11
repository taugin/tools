#!/usr/bin/python
# coding: UTF-8
import os
import sys
import getopt
import zipfile
import hashlib
import subprocess

SEPERATER = os.path.sep
SIGNINFO_MD5 = False
CLASSES_MD5 = False
KEYTOOL = "keytool"

def log(str, show=True):
    if (show):
        print(str)

def md5_classes(apkFile):
    signfile = ""
    z = zipfile.ZipFile(apkFile, "r")
    for f in z.namelist() :
        if (f == "classes.dex"):
            signfile = f
    if (signfile != ""):
        retsult = hashlib.md5(z.read(signfile)).hexdigest()
        log("[CLASSDEX] " + retsult + " : " + apkFile)
    z.close()


def printsign_md5(apkFile, signFile):
    cmdlist = [KEYTOOL, "-printcert", "-file", signFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    process.wait()
    alllines = process.stdout.readlines()
    for line in alllines:
        tmp = str(line, "gbk")
        tmp = tmp.strip().lower()
        if (tmp.startswith("md5")):
            tmp = tmp[4:]
            tmp = tmp.replace(":", "")
            log("[SIGNFILE] " + tmp + " : " + apkFile)

def md5_signfile(apkFile):
    signfile = ""
    z = zipfile.ZipFile(apkFile, "r")
    for f in z.namelist() :
        if (len(f) >=2 and f[-2:] == "SA"):
            signfile = f
    if (signfile != ""):
        tmpfile = os.path.basename(signfile)
        f = open(tmpfile, "wb");
        f.write(z.read(signfile));
        f.close()
        printsign_md5(apkFile, tmpfile)
        os.remove(tmpfile)
    z.close()

def getpkg(apkFile):
    cmdlist = ["aapt", "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    retcode = process.wait()
    if (retcode != 0):
        log("aapt命令执行失败")
        sys.exit()

    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = str(line, "utf-8")
        if (tmp.startswith("package")):
            break;
    tmp = str(line, "utf-8")
    tmp = tmp.replace("\r", "")
    tmp = tmp.replace("\n", "")
    log(tmp)

def readapkinfo(apkFile, function):
    function(apkFile)

def processapk(args, function):
    for file in args :
        if (os.path.isdir(file)):
            listfiles = os.listdir(file)
            for apkfile in listfiles :
                apkpath = file + SEPERATER + apkfile
                if (len(apkpath) >= 4 and apkpath[-4:] == ".apk"):
                    readapkinfo(os.path.abspath(apkpath), function)
        else:
            if (len(file) >= 4 and file[-4:] == ".apk"):
                readapkinfo(os.path.abspath(file), function)

if (len(sys.argv) < 2):
    log("[Logging...] 缺少参数")
    log("[Logging...] %s [-c] <src_apk> 输出classes.dex MD5值" % os.path.basename(sys.argv[0]), True);
    log("[Logging...] %s [-s] <src_apk> 输出APK文件签名 MD5值" % os.path.basename(sys.argv[0]), True);
    log("[Logging...] %s <src_apk> 输出APK文件信息" % os.path.basename(sys.argv[0]), True);

try:
    opts, args = getopt.getopt(sys.argv[1:], "sc")
    for op, value in opts:
        if (op == "-c"):
            CLASSES_MD5 = True
        elif (op == "-s"):
            SIGNINFO_MD5 = True
except getopt.GetoptError as err:
    log(err)
    sys.exit()

if (CLASSES_MD5 == True):
    log("显示classes.dex的MD5值 : ")
    processapk(args, md5_classes)
if (SIGNINFO_MD5 == True):
    log("显示APK文件签名的MD5值 : ")
    processapk(args, md5_signfile)
if (CLASSES_MD5 == False and SIGNINFO_MD5 == False):
    log("显示包文件是的包名信息 : ")
    processapk(args, getpkg)