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

import io
import re
import getopt
import zipfile
import hashlib
import platform
import subprocess

SIGNINFO_MD5 = False
FILE_MD5 = False
STR_MD5 = False
APK_INFO = False
INSTALL_APK = False
AXMLPRINTER = False

def md5_classes(apkFile):
    signfile = ""
    z = zipfile.ZipFile(apkFile, "r")
    for f in z.namelist() :
        if (f == "classes.dex"):
            signfile = f
    if (signfile != ""):
        retsult = hashlib.md5(z.read(signfile)).hexdigest()
        Log.out("[CLASSDEX] " + retsult + " : " + apkFile)
    z.close()


def printsign_md5(apkFile, signFile):
    cmdlist = [Common.KEYTOOL, "-printcert", "-file", signFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    process.wait()
    alllines = process.stdout.readlines()
    for line in alllines:
        tmp = str(line, "gbk")
        tmp = tmp.strip().lower()
        if (tmp.startswith("md5")):
            tmp = tmp[4:]
            tmp = tmp.replace(":", "").strip()
            Log.out("[SIGNFILE] " + tmp + " : " + apkFile)

def md5_signfile(apkFile):
    signfile = ""
    z = zipfile.ZipFile(apkFile, "r")
    for f in z.namelist() :
        if (len(f) >=2 and f[-2:] == "SA"):
            signfile = f
            break;
    if (signfile != ""):
        tmpfile = os.path.basename(signfile)
        f = open(tmpfile, "wb");
        f.write(z.read(signfile));
        f.close()
        printsign_md5(apkFile, tmpfile)
        os.remove(tmpfile)
    z.close()

def getpkg(apkFile):
    cmdlist = [Common.AAPT_BIN, "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)

    tmppkg = ""
    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = str(line, "utf-8")
        if (tmp.startswith("package")):
            tmppkg = tmp
            break;
    tmppkg = tmppkg.replace("\r", "")
    tmppkg = tmppkg.replace("\n", "")
    tmppkg = tmppkg.replace("'", "")
    Log.out("apkfile: " + apkFile)
    Log.out(tmppkg)
    #Log.out("--------------------------------------------")

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
    Log.out("apkfile: " + apkFile)
    Log.out(tmppkg)
    #Log.out("--------------------------------------------")

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
    Log.out("[MD5..] " + md5value + " : " + strFile)

def string_md5(srcStr):
    if (len(srcStr) > 0):
        md5=hashlib.md5(srcStr[0].encode('utf-8')).hexdigest()
        Log.out("[MD5..] " + md5)
    else:
        Log.out("[Logging...] 缺少参数")

def check_arg(args):
    if (len(args) > 0):
        for arg in args:
            if (os.path.isfile(arg) == False and os.path.isdir(arg) == False):
                Log.out("[Logging...] " + os.path.abspath(arg) + " 不是目录或文件")
                args.remove(arg)
    Log.out("")
    if (len(args) <= 0):
        Log.out("[Logging...] 缺少文件")
        sys.exit()

def install_apk(args):
    if (len(args) > 0):
        cmd = [Common.ADB, "-d", "install", "-r", args[0]]
        Log.out("正在安装 : " + os.path.abspath(args[0]))
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        execret = result.stdout.readlines();
        allret = ""
        success = False
        for s in execret:
            s = str(s, "utf-8")
            s = s.replace("\r", "")
            s = s.replace("\n", "")
            allret = allret + s + "\n"
            if (s.lower() == "success"):
                success = True
        Log.out(allret)
        if (success == False):
            Common.pause()

def print_xml(args):
    manifest = ""
    if (len(args) > 0):
        if (len(args[0]) >= 4 and args[0][-4:] == ".apk"):
            zf = zipfile.ZipFile(os.path.abspath(args[0]), "r")
            for file in zf.namelist():
                if (file == "AndroidManifest.xml"):
                    manifest = file
                    break;
            if (manifest != ""):
                tmpfile = os.path.basename(manifest)
                f = open(tmpfile, "wb");
                f.write(zf.read(manifest));
                f.close()
                cmd = [Common.JAVA, "-jar", Common.AXMLPRINTER_JAR, tmpfile]
                subprocess.call(cmd)
                os.remove(tmpfile)
            zf.close()

# start ============================================================================================
if (len(sys.argv) < 2):
    Log.out("[Logging...] 缺少参数 : %s <src_apk> 输出APK文件信息" % os.path.basename(sys.argv[0]), True);
    sys.exit()

try:
    opts, args = getopt.getopt(sys.argv[1:], "pmsia")
    for op, value in opts:
        if (op == "-m"):
            FILE_MD5 = True
        elif (op == "-s") :
            STR_MD5 = True
        elif (op == "-p") :
            APK_INFO = True
        elif (op == "-i") :
            INSTALL_APK = True
        elif (op == "-a") :
            AXMLPRINTER = True
except getopt.GetoptError as err:
    Log.out(err)
    sys.exit()
#安装apk
if INSTALL_APK == True:
    install_apk(args)
    sys.exit()
#打印Android xml 文件
if AXMLPRINTER == True:
    print_xml(args)
    sys.exit()
#求字符串的MD5值
if STR_MD5 == True:
    string_md5(args)
    sys.exit()

check_arg(args)

if FILE_MD5 == True:
    processFileMd5(args)

if APK_INFO == True:
    Log.out("显示包文件是的应用名称 : ")
    #Log.out("--------------------------------------------")
    processapk(args, getlabel)
    Log.out("\n")

    Log.out("显示包文件是的包名信息 : ")
    #Log.out("--------------------------------------------")
    processapk(args, getpkg)
    Log.out("\n")

    Log.out("显示classes.dex的MD5值 : ")
    #Log.out("--------------------------------------------")
    processapk(args, md5_classes)
    Log.out("\n")
    #Log.out("--------------------------------------------")

    Log.out("显示APK文件签名的MD5值 : ")
    #Log.out("--------------------------------------------")
    processapk(args, md5_signfile)
    Log.out("\n")
    #Log.out("--------------------------------------------")

    Log.out("显示APK文件的MD5值 : ")
    #Log.out("--------------------------------------------")
    processapk(args, file_md5)
    #Log.out("--------------------------------------------")
Common.pause()