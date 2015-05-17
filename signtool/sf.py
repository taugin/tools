#!/usr/bin/python
# coding: UTF-8
import os
import io
import re
import sys
import hashlib
import getopt
import zipfile
import hashlib
import subprocess

SIGNINFO_MD5 = False
FILE_MD5 = False
STR_MD5 = False
APK_INFO = False
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
            tmp = tmp.replace(":", "").strip()
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
    tmp = tmp.lower()
    m = re.match(r".*name='(.+)'\s+versioncode='(.+)'\s+versionname='(.+)'", tmp)
    if m:
        (packagename, versioncode, versionname) = m.groups()
    result =  "packagefile : " + apkFile + "\n"
    result += "packagename : " + packagename + "\n"
    result += "versioncode : " + versioncode + "\n"
    result += "versionname : " + versionname
    log(result)
    log("--------------------------------------------")

def readapkinfo(apkFile, function):
    function(apkFile)

def processapk(args, function):
    for file in args :
        if (os.path.isdir(file)):
            listfiles = os.listdir(file)
            for apkfile in listfiles :
                apkpath = os.path.join(file, apkfile)
                if (len(apkpath) >= 4 and apkpath[-4:] == ".apk"):
                    readapkinfo(os.path.abspath(apkpath), function)
        else:
            if (len(file) >= 4 and file[-4:] == ".apk"):
                readapkinfo(os.path.abspath(file), function)

def processFileMd5(args):
    for file in args :
        if (os.path.isdir(file)):
            listfiles = os.listdir(file)
            for apkfile in listfiles :
                apkpath = os.path.join(file, apkfile)
                if (os.path.isfile(os.path.abspath(apkpath))):
                    file_md5(os.path.abspath(apkpath))
        else:
            if (os.path.isfile(os.path.abspath(file))):
                file_md5(os.path.abspath(file))

def file_md5(strFile):
    m = hashlib.md5()
    file = io.FileIO(strFile,'rb')
    bytes = file.read(1024)
    while(bytes != b''):
        m.update(bytes)
        bytes = file.read(1024)
    file.close()
    md5value = m.hexdigest()
    log("[MD5..] " + md5value + " : " + strFile)

def string_md5(srcStr):
    if (len(srcStr) > 0):
        md5=hashlib.md5(srcStr[0].encode('utf-8')).hexdigest()
        log("[MD5..] " + md5)
    else:
        log("[Logging...] 缺少参数")

def check_arg(args):
    if (len(args) > 0):
        for arg in args:
            if (os.path.isfile(arg) == False and os.path.isdir(arg) == False):
                log("[Logging...] " + os.path.abspath(arg) + " 不是目录或文件")
                args.remove(arg)
    log("")
    if (len(args) <= 0):
        log("[Logging...] 缺少文件")
        sys.exit()
# start ============================================================================================
if (len(sys.argv) < 2):
    log("[Logging...] 缺少参数 : %s <src_apk> 输出APK文件信息" % os.path.basename(sys.argv[0]), True);
    sys.exit()

try:
    opts, args = getopt.getopt(sys.argv[1:], "pms")
    for op, value in opts:
        if (op == "-m"):
            FILE_MD5 = True
        elif (op == "-s") :
            STR_MD5 = True
        elif (op == "-p") :
            APK_INFO = True
except getopt.GetoptError as err:
    log(err)
    sys.exit()

#求字符串的MD5值
if STR_MD5 == True:
    string_md5(args)
    sys.exit()

check_arg(args)

if FILE_MD5 == True:
    processFileMd5(args)

if APK_INFO == True:
    log("显示包文件是的包名信息 : ")
    log("--------------------------------------------")
    processapk(args, getpkg)

    log("显示classes.dex的MD5值 : ")
    log("--------------------------------------------")
    processapk(args, md5_classes)
    log("--------------------------------------------")

    log("显示APK文件签名的MD5值 : ")
    log("--------------------------------------------")
    processapk(args, md5_signfile)
    log("--------------------------------------------")
os.system("pause")