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
import msvcrt

SIGNINFO_MD5 = False
FILE_MD5 = False
STR_MD5 = False
APK_INFO = False
INSTALL_APK = False
AXMLPRINTER = False
KEYTOOL = "keytool"
ADB = "adb"
JAVA = "java"

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
    cmdlist = ["aapt", "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)

    tmppkg = ""
    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = str(line, "utf-8")
        if (tmp.startswith("package")):
            tmppkg = tmp
            break;
    tmppkg = str(line, "utf-8")
    tmppkg = tmppkg.replace("\r", "")
    tmppkg = tmppkg.replace("\n", "")
    tmppkg = tmppkg.replace("'", "")
    log("apkfile: " + apkFile)
    log(tmppkg)
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

def install_apk(args):
    if (len(args) > 0):
        cmd = [ADB, "install", "-r", args[0]]
        log("正在安装 : " + os.path.abspath(args[0]))
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
        log(allret)
        if (success == False):
            log("操作完成，按任意键退出", True)
            msvcrt.getch()

def print_xml(args):
    manifest = ""
    jarfile = os.path.join(os.path.dirname(sys.argv[0]), "AXMLPrinter2.jar")
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
                log(jarfile)
                cmd = [JAVA, "-jar", jarfile, tmpfile]
                subprocess.call(cmd)
                os.remove(tmpfile)
            zf.close()

# start ============================================================================================
if (len(sys.argv) < 2):
    log("[Logging...] 缺少参数 : %s <src_apk> 输出APK文件信息" % os.path.basename(sys.argv[0]), True);
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
    log(err)
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
log("操作完成，按任意键退出", True)
msvcrt.getch()