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
import getopt
import zipfile
import hashlib
import subprocess
import re
import time

SIGNINFO_MD5 = False
FILE_MD5 = False
STR_MD5 = False
APK_INFO = False
INSTALL_APK = False
AXMLPRINTER = False
apk_info = {}
apk_info["apkfile"] = None
apk_info["apklabel"] = None
apk_info["pkgname"] = None
apk_info["vercode"] = None
apk_info["vername"] = None
apk_info["classes_md5"] = None
apk_info["apk_md5"] = None
apk_info["apk_sha1"] = None
apk_info["sign_md5"] = None
apk_info["sign_sha1"] = None
apk_info["sign_sha256"] = None
apk_info["apk_size"] = None

def md5_classes(apkFile):
    '''    输出classes.dex的MD5    '''
    global apk_info
    signfile = ""
    z = zipfile.ZipFile(apkFile, "r")
    for f in z.namelist() :
        if (f == "classes.dex"):
            signfile = f
    if (signfile != ""):
        result = hashlib.md5(z.read(signfile)).hexdigest()
        apk_info["classes_md5"] = result
    z.close()

def printsign_md5(apkFile, signFile):
    '''输出签名文件的MD5'''
    global apk_info
    cmdlist = [Common.KEYTOOL, "-printcert", "-file", signFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
    process.wait()
    alllines = process.stdout.readlines()
    sign_md5 = None
    sign_sha256 = None
    sign_sha1 = None
    for line in alllines:
        tmp = str(line, "gbk")
        tmp = tmp.strip().lower()
        if (tmp.startswith("md5")):
            tmp = tmp[len("md5") + 1:]
            sign_md5 = tmp.replace(":", "").strip()
        if (tmp.startswith("sha256")):
            tmp = tmp[len("sha256") + 1:]
            sign_sha256 = tmp.strip()
        if (tmp.startswith("sha1")):
            tmp = tmp[len("sha1") + 1:]
            sign_sha1 = tmp.strip()
    apk_info["sign_md5"] = sign_md5
    apk_info["sign_sha256"] = sign_sha256
    apk_info["sign_sha1"] = sign_sha1

def md5_signfile(apkFile):
    '''输出一般文件的MD5'''
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
    '''输出apk的包信息'''
    global apk_info
    cmdlist = [Common.AAPT_BIN, "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)

    tmppkg = ""
    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = str(line, "utf-8")
        if (tmp.startswith("package: ")):
            tmppkg = tmp[len("package: "):]
            break;
    tmppkg = tmppkg.replace("\r", "")
    tmppkg = tmppkg.replace("\n", "")
    tmppkg = tmppkg.replace("'", "")
    tmpsplit = tmppkg.split(" ")
    pkgname = None
    vercode = None
    vername = None
    if tmpsplit != None and len(tmpsplit) >= 3:
        pkgname = tmpsplit[0].split("=")[1]
        vercode = tmpsplit[1].split("=")[1]
        vername = tmpsplit[2].split("=")[1]
    apk_info["pkgname"] = pkgname
    apk_info["vercode"] = vercode
    apk_info["vername"] = vername

def getlabel(apkFile):
    global apk_info
    apk_info["apkfile"] = apkFile
    cmdlist = [Common.AAPT_BIN, "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)

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
    apk_info["apklabel"] = label

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
                    file_sh1(os.path.abspath(apkpath))
        else:
            if (os.path.isfile(os.path.abspath(file))):
                file_md5(os.path.abspath(file))
                file_sh1(os.path.abspath(file))

def formatSize(bytesLen):
    try:
        bytesLen = float(bytesLen)
        kb = bytesLen / 1024
    except:
        print("传入的字节格式不对")
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fG" % (G)
        else:
            return "%.2fM" % (M)
    else:
        return "%.2fkb" % (kb)

def file_md5(strFile):
    global apk_info
    m = hashlib.md5()
    file = io.FileIO(strFile,'rb')
    bytesRead = file.read(1024)
    while(bytesRead != b''):
        m.update(bytesRead)
        bytesRead = file.read(1024)
    file.close()
    md5value = m.hexdigest()
    apk_info["apk_md5"] = md5value

def file_sh1(strFile):
    global apk_info
    sha1 = hashlib.sha1()
    file = io.FileIO(strFile,'rb')
    bytesRead = file.read(1024)
    while(bytesRead != b''):
        sha1.update(bytesRead)
        bytesRead = file.read(1024)
    file.close()
    sh1value = sha1.hexdigest()
    apk_info["apk_sha1"] = sh1value

def file_size(strFile):
    try:
        size = os.path.getsize(strFile)
        apk_info["apk_size"] = formatSize(size)
    except:
        pass
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

def input_no(start, end):
    try:
        while True:
            i = input("请输入设备顺序 : ")
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
                no = input_no(1, len(devices))
            return devices[int(no) - 1][0]
    except:
        pass
    return None
def install_apk(args):
    if (len(args) > 0):
        cmd = [Common.ADB, "-d", "install", "-r", args[0]]
        device = get_select_devices()
        if device != None and len(device) > 0 :
            cmd = [Common.ADB, "-s", device, "install", "-r", args[0]]
            Log.out("[Logging...] 正在安装 : [%s] %s" % (device, os.path.abspath(args[0])))
        elif device == None:
            Log.out("[Logging...] 没有发现设备")
            time.sleep(2)
            return
        else:
            Log.out("[Logging...] 正在安装 : " + os.path.abspath(args[0]))
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
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
        else:
            time.sleep(2)

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

def calc_maxlen():
    global apk_info
    max_len = 0
    for key in apk_info:
        if apk_info[key] != None:
            ilen = len(apk_info[key])
            if ilen > max_len:
                max_len = ilen
    return max_len

def print_apkinfo():
    global apk_info
    max_len = calc_maxlen()
    dash_len = 13 + max_len
    Log.out("-" * dash_len)
    output = " 文件名称 | %s" % apk_info["apkfile"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 应用名称 | %s" % apk_info["apklabel"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 应用包名 | %s" % apk_info["pkgname"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 应用版本 | %s" % apk_info["vercode"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 应用版本 | %s " % apk_info["vername"]
    Log.out(output)
    
    Log.out("-" * dash_len)
    output = " 文件大小 | %s " % apk_info["apk_size"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 内部摘要 | %s" % apk_info["classes_md5"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名摘要 | %s" % apk_info["sign_md5"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名哈希 | %s" % apk_info["sign_sha256"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名哈希 | %s" % apk_info["sign_sha1"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 文件摘要 | %s" % apk_info["apk_md5"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 文件哈希 | %s" % apk_info["apk_sha1"]
    Log.out(output)
    Log.out("-" * dash_len)

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
    max_len = calc_maxlen()
    dash_len = 13 + max_len
    Log.out("-" * dash_len)
    output = " 文件摘要 | %s" % apk_info["apk_md5"]
    output +="\n"
    output += " 文件哈希 | %s" % apk_info["apk_sha1"]
    Log.out(output)
    Log.out("-" * dash_len)
elif APK_INFO == True:
    processapk(args, getlabel)
    processapk(args, getpkg)
    processapk(args, file_size)
    processapk(args, md5_classes)
    processapk(args, md5_signfile)
    processapk(args, file_md5)
    processapk(args, file_sh1)
    print_apkinfo()
    Log.out("")
Common.pause()