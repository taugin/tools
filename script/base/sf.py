#!/usr/bin/python
# coding: UTF-8
from threading import Thread
import time
import re
import subprocess
import hashlib
import zipfile
import getopt
import io
import sys
import os
# 引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import Utils
import Log
import Common

SIGNINFO_MD5 = False
FILE_MD5 = False
STR_MD5 = False
APK_INFO = False
INSTALL_APK = False
INSTALL_XAPK = False
AXMLPRINTER = False
OPEN_IN_GP = False
CHECK_PROCESS = False
apk_info = {}
apk_info["apkfile"] = None
apk_info["apklabel"] = None
apk_info["pkgname"] = None
apk_info["vercode"] = None
apk_info["vername"] = None
apk_info["classes_md5"] = None
apk_info["apk_md5"] = None
apk_info["apk_sha1"] = None
apk_info["apk_sha256"] = None
apk_info["sign_md5"] = None
apk_info["sign_sha1"] = None
apk_info["sign_sha256"] = None
apk_info["sign_file"] = None
apk_info["apk_size"] = None
apk_info["target_version"] = None
apk_info["min_version"] = None
apk_info["sign_detail"] = None


def addColonForString(ori_string):
    step = 2
    size = len(ori_string)
    dst_string = ""
    index = 0
    for s in ori_string:
        dst_string += s
        if (index % 2 == 1 and index < size - 1):
            dst_string += ":"
        index += 1
    return dst_string

def file_sign_info(keystorefilepath):
    filedir = os.path.dirname(keystorefilepath)
    keystorefile = os.path.basename(keystorefilepath)
    Log.out("[Logging...] 签名文件 : %s" % keystorefile, True)
    keystorename = os.path.basename(keystorefile)
    index = keystorename.rfind(".keystore")
    if index < 0:
        index = keystorename.rfind(".jks")
    if index < 0:
        Log.out("[Logging...] 不是一个有效的签名文件 : %s" % keystorefile, True)
        return None
    filename = keystorename[0:index]
    splits = filename.split("_")
    if (len(splits) < 3):
        Log.out("[Logging...] 无法获取签名文件信息,请重命名签名文件格式 <[alias]_[storepass]_[aliaspass].keystore/jks>", True)
        return None
    keystorealias = splits[0]
    if (splits[1] != "pwd"):
        keystorepass = splits[1]
    else:
        keystorepass = splits[2]

    if (keystorealias == "" or keystorepass == ""):
        Log.out("[Logging...] keystorealias or keystorepass is empty")
        sys.exit()

    global apk_info
    keystorepath = os.path.normpath(os.path.join(filedir, keystorefile))
    if Common.KEYTOOL == None or len(Common.KEYTOOL) <= 0 or not os.path.exists(Common.KEYTOOL):
        Log.out("[Logging...] 签名程序路径 : 无法找到签名文件 [keytool]")
    else:
        p = subprocess.Popen([Common.KEYTOOL, "-v", "-list", "-keystore", keystorepath, "-storepass", keystorepass], stdout=subprocess.PIPE)
        alllines = p.stdout.readlines()
        for line in alllines:
            tmp = Utils.parseString(line)
            tmp = tmp.replace("\r", "")
            tmp = tmp.replace("\n", "")
            tmp = tmp.strip()
            if tmp.startswith('MD5:'):
                apk_info['sign_md5'] = tmp.replace("MD5:", "").strip()
            if tmp.startswith('SHA1:'):
                apk_info['sign_sha1'] = tmp.replace("SHA1:", "").strip()
            if tmp.startswith('SHA256:'):
                apk_info['sign_sha256'] = tmp.replace("SHA256:", "").strip()

def md5_classes(apkFile):
    '''    输出classes.dex的MD5    '''
    global apk_info
    signfile = ""
    z = zipfile.ZipFile(apkFile, "r")
    for f in z.namelist():
        if (f == "classes.dex"):
            signfile = f
    if (signfile != ""):
        result = hashlib.md5(z.read(signfile)).hexdigest()
        apk_info["classes_md5"] = addColonForString(result.upper())
    z.close()


def printsign_md5_with_jarsigner(apkFile):
    '''输出签名文件的MD5'''
    global apk_info
    if Common.KEYTOOL == None or len(Common.KEYTOOL) <= 0 or not os.path.exists(Common.KEYTOOL):
        Log.out("[Logging...] 签名程序路径 : 无法找到签名文件 [keytool]")
        return
    if apkFile != None and os.path.exists(apkFile):
        cmdlist = [Common.KEYTOOL, "-printcert", "-jarfile", apkFile]
        Utils.printExecCmdString(cmdlist)
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)
        process.wait()
        alllines = process.stdout.readlines()
        sign_md5 = None
        sign_sha256 = None
        sign_sha1 = None
        for line in alllines:
            tmp = str(line, "gbk")
            if tmp != None and tmp.startswith("所有者:"):
                apk_info["sign_detail"] = tmp.replace("所有者: ", "").replace("\n", "")
            tmp = tmp.strip().lower()
            if (tmp.startswith("md5")):
                tmp = tmp[len("md5") + 1:]
                sign_md5 = tmp.replace(":", ":").strip().upper()
            if (tmp.startswith("sha256")):
                tmp = tmp[len("sha256") + 1:]
                sign_sha256 = tmp.strip().upper()
            if (tmp.startswith("sha1")):
                tmp = tmp[len("sha1") + 1:]
                sign_sha1 = tmp.strip().upper()
        apk_info["sign_md5"] = sign_md5
        apk_info["sign_sha256"] = sign_sha256
        apk_info["sign_sha1"] = sign_sha1

def printsign_md5_with_apksigner(apkFile):
    cmdlist = [Common.JAVA, "-jar", Common.APKSIGNER, "verify", "-print-certs", apkFile]
    Utils.printExecCmdString(cmdlist)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)
    #process.wait()
    alllines = process.stdout.readlines()
    sign_md5 = None
    sign_sha256 = None
    sign_sha1 = None
    sign_detail = None
    for line in alllines:
        tmp = str(line, "gbk")
        tmp = tmp.strip()
        if (tmp.startswith("Signer #1 certificate MD5 digest:")):
            tmp = tmp[len("Signer #1 certificate MD5 digest:") + 1:]
            tmp = tmp.strip().upper()
            tmp_list = []
            length = len(tmp)
            for index in range(0, length):
                tmp_list.append(tmp[index])
                if index % 2 == 1 and index < length - 1:
                    tmp_list.append(":")
            sign_md5 = "".join(tmp_list)
        elif (tmp.startswith("Signer #1 certificate SHA-1 digest:")):
            tmp = tmp[len("Signer #1 certificate SHA-1 digest:") + 1:]
            tmp = tmp.strip().upper()
            tmp_list = []
            length = len(tmp)
            for index in range(0, length):
                tmp_list.append(tmp[index])
                if index % 2 == 1 and index < length - 1:
                    tmp_list.append(":")
            sign_sha1 = "".join(tmp_list)
        elif (tmp.startswith("Signer #1 certificate SHA-256 digest:")):
            tmp = tmp[len("Signer #1 certificate SHA-256 digest:") + 1:]
            tmp = tmp.strip().upper()
            tmp_list = []
            length = len(tmp)
            for index in range(0, length):
                tmp_list.append(tmp[index])
                if index % 2 == 1 and index < length - 1:
                    tmp_list.append(":")
            sign_sha256 = "".join(tmp_list)
        elif (tmp.startswith("Signer #1 certificate DN:")):
            sign_detail = tmp[len("Signer #1 certificate DN:") + 1:]
    apk_info["sign_md5"] = sign_md5
    apk_info["sign_sha256"] = sign_sha256
    apk_info["sign_sha1"] = sign_sha1
    apk_info["sign_detail"] = sign_detail

def md5_signfile(apkFile):
    '''输出一般文件的MD5'''
    if apkFile != None and apkFile.endswith(".apk"):
        printsign_md5_with_apksigner(apkFile)
    if apk_info["sign_md5"] == None or len(apk_info["sign_md5"]) <= 0:
        printsign_md5_with_jarsigner(apkFile)


def get_app_info(apkFile):
    '''输出apk的包信息'''
    global apk_info
    apk_info["apkfile"] = apkFile
    apkname, ext = os.path.splitext(apkFile)
    if ext == ".apk":
        cmdlist = [Common.AAPT2_BIN, "d", "badging", apkFile]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
        tmppkg = ""
        tmp = ""
        alllines = process.stdout.readlines()
        for line in alllines:
            tmp = Utils.parseString(line)
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
    elif ext == ".xapk":
        jobj = readpkgnamefromxapk(apkFile)
        apk_info["apklabel"] = jobj["name"] if "name" in jobj else None
        apk_info["pkgname"] = jobj["package_name"] if "package_name" in jobj else None
        apk_info["vercode"] = jobj["version_code"] if "version_code" in jobj else None
        apk_info["vername"] = jobj["version_name"] if "version_name" in jobj else None
        apk_info["min_version"] = jobj["min_sdk_version"] if "min_sdk_version" in jobj else None
        apk_info["target_version"] = jobj["target_sdk_version"] if "target_sdk_version" in jobj else None
    elif ext == ".aab":
        cmdlist = [Common.JAVA, "-jar", Common.BUNDLE_TOOL, "dump", "manifest", "--bundle", apkFile, "--xpath", "/manifest/@package"]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
        process.wait()
        apk_info["pkgname"] = Utils.parseString(process.stdout.readline()).strip()
        cmdlist = [Common.JAVA, "-jar", Common.BUNDLE_TOOL, "dump", "manifest", "--bundle", apkFile, "--xpath", "/manifest/@android:versionCode"]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
        process.wait()
        apk_info["vercode"] = Utils.parseString(process.stdout.readline()).strip()
        cmdlist = [Common.JAVA, "-jar", Common.BUNDLE_TOOL, "dump", "manifest", "--bundle", apkFile, "--xpath", "/manifest/@android:versionName"]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
        process.wait()
        apk_info["vername"] = Utils.parseString(process.stdout.readline()).strip()
        cmdlist = [Common.JAVA, "-jar", Common.BUNDLE_TOOL, "dump", "manifest", "--bundle", apkFile, "--xpath", "/manifest/uses-sdk/@android:minSdkVersion"]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
        process.wait()
        apk_info["min_version"] = Utils.parseString(process.stdout.readline()).strip()
        cmdlist = [Common.JAVA, "-jar", Common.BUNDLE_TOOL, "dump", "manifest", "--bundle", apkFile, "--xpath", "/manifest/uses-sdk/@android:targetSdkVersion"]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=True)
        process.wait()
        apk_info["target_version"] = Utils.parseString(process.stdout.readline()).strip()


def readapkinfo(apkFile, function):
    function(apkFile)


def processapk(args, function):
    for file in args:
        if (os.path.isdir(file)):
            listfiles = os.listdir(file)
            for apkfile in listfiles:
                apkpath = os.path.join(file, apkfile)
                apkname, ext = os.path.splitext(apkpath)
                if ext == ".apk" or ext == ".xapk" or ext == ".aab":
                    readapkinfo(os.path.abspath(apkpath), function)
        else:
            apkname, ext = os.path.splitext(file)
            if ext == ".apk" or ext == ".xapk" or ext == ".aab":
                readapkinfo(os.path.abspath(file), function)


def processFileMd5(args):
    global apk_info
    for file in args:
        if (os.path.isdir(file)):
            listfiles = os.listdir(file)
            for apkfile in listfiles:
                apkpath = os.path.join(file, apkfile)
                if (os.path.isfile(os.path.abspath(apkpath))):
                    apk_info["apk_file"] = os.path.abspath(apkpath)
                    file_md5(os.path.abspath(apkpath))
                    file_sh1(os.path.abspath(apkpath))
                    file_sh256(os.path.abspath(apkpath))
                    file_sign_info(os.path.abspath(apkpath))
        else:
            if (os.path.isfile(os.path.abspath(file))):
                apk_info["apk_file"] = os.path.abspath(file)
                file_md5(os.path.abspath(file))
                file_sh1(os.path.abspath(file))
                file_sh256(os.path.abspath(file))
                file_sign_info(os.path.abspath(file))


def formatSize(bytesLen):
    """格式化文件大小"""
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
    """计算文件md5"""
    global apk_info
    m = hashlib.md5()
    file = io.FileIO(strFile, 'rb')
    bytesRead = file.read(1024)
    while(bytesRead != b''):
        m.update(bytesRead)
        bytesRead = file.read(1024)
    file.close()
    md5value = m.hexdigest()
    apk_info["apk_md5"] = addColonForString(md5value.upper())


def file_sh1(strFile):
    """计算文件hash"""
    global apk_info
    sha1 = hashlib.sha1()
    file = io.FileIO(strFile, 'rb')
    bytesRead = file.read(1024)
    while(bytesRead != b''):
        sha1.update(bytesRead)
        bytesRead = file.read(1024)
    file.close()
    sh1value = sha1.hexdigest()
    apk_info["apk_sha1"] = addColonForString(sh1value.upper())


def file_sh256(strFile):
    """计算文件hash256"""
    global apk_info
    sha256 = hashlib.sha256()
    file = io.FileIO(strFile, 'rb')
    bytesRead = file.read(1024)
    while(bytesRead != b''):
        sha256.update(bytesRead)
        bytesRead = file.read(1024)
    file.close()
    sh256value = sha256.hexdigest()
    apk_info["apk_sha256"] = addColonForString(sh256value.upper())


def file_size(strFile):
    """计算文件大小"""
    try:
        size = os.path.getsize(strFile)
        apk_info["apk_size"] = formatSize(size)
    except:
        pass


def string_md5(srcStr):
    """计算字符串的md5值"""
    if (len(srcStr) > 0):
        md5 = hashlib.md5(srcStr[0].encode('utf-8')).hexdigest()
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
                no = input_no(1, len(devices))
            return devices[int(no) - 1][0]
    except:
        pass
    return None


def install_apk(args):
    if (len(args) > 0):
        cmd = [Common.ADB, "-d", "install", "-t", "-r", args[0]]
        device = get_select_devices()
        if device != None and len(device) > 0:
            cmd = [Common.ADB, "-s", device, "install", "-t", "-r", args[0]]
            Log.out("[Logging...] 正在安装 : [%s] %s" %
                    (device, os.path.abspath(args[0])))
        elif device == None:
            Log.out("[Logging...] 没有发现设备")
            time.sleep(2)
            return
        else:
            Log.out("[Logging...] 正在安装 : " + os.path.abspath(args[0]))
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
        execret = result.stdout.readlines()
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


def install_multiple_apks(xapk, apks):
    if (len(apks) > 0):
        cmd = [Common.ADB, "-d", "install-multiple", "-t", "-r"] + apks
        device = get_select_devices()
        if device != None and len(device) > 0:
            cmd = [Common.ADB, "-s", device,
                   "install-multiple", "-t", "-r"] + apks
            Log.out("[Logging...] 正在安装 : [%s] %s" %
                    (device, os.path.abspath(xapk)))
        elif device == None:
            Log.out("[Logging...] 没有发现设备")
            time.sleep(2)
            return
        else:
            Log.out("[Logging...] 正在安装 : %s" % os.path.abspath(xapk))
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
        execret = result.stdout.readlines()
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


def install_xapk(args):
    if (len(args) > 0):
        basefilename, ext = os.path.splitext(os.path.basename(args[0]))
        if not os.path.exists(basefilename):
            os.mkdir(basefilename)
        zf = zipfile.ZipFile(os.path.abspath(args[0]), "r")
        apklist = []
        for file in zf.namelist():
            if (file != None and file.endswith(".apk")):
                apklist += [os.path.join(os.getcwd(), basefilename, file)]
                zf.extract(file, basefilename)
        install_multiple_apks(args[0], apklist)
        Log.out("[Logging...] 删除临时文件 : %s" % basefilename)
        Utils.deletedir(basefilename)
        time.sleep(2)


def print_xml(args):
    manifest = ""
    if (len(args) > 0):
        if (len(args[0]) >= 4 and args[0][-4:] == ".apk"):
            zf = zipfile.ZipFile(os.path.abspath(args[0]), "r")
            for file in zf.namelist():
                if (file == "AndroidManifest.xml"):
                    manifest = file
                    break
            if (manifest != ""):
                tmpfile = os.path.basename(manifest)
                f = open(tmpfile, "wb")
                f.write(zf.read(manifest))
                f.close()
                cmd = [Common.JAVA, "-jar", Common.AXMLPRINTER_JAR, tmpfile]
                subprocess.call(cmd)
                os.remove(tmpfile)
            zf.close()


def readpkgnamefromxapk(xapk_path):
    try:
        zf = zipfile.ZipFile(xapk_path, "r")
        content = zf.read("manifest.json")
        zf.close()
        import json
        return json.loads(content)
    except:
        pass
    return {}


def get_package_name(args):
    global apk_info
    apk_path = None
    xapk_path = None
    pkgname = None
    for file in args:
        apkname, ext = os.path.splitext(file)
        if (ext == ".apk"):
            apk_path = os.path.abspath(file)
            break
        elif (ext == ".xapk"):
            xapk_path = os.path.abspath(file)
            break

    if (apk_path != None and len(apk_path) > 0):
        output = "[Logging...] 当前应用路径 : [%s]" % apk_path
        Log.out(output)
        get_app_info(apk_path)
        pkgname = apk_info["pkgname"]
    elif (xapk_path != None and len(xapk_path) > 0):
        output = "[Logging...] 当前应用路径 : [%s]" % xapk_path
        Log.out(output)
        xapkobj = readpkgnamefromxapk(xapk_path)
        pkgname = xapkobj["package_name"]
    output = "[Logging...] 当前应用包名 : [%s]" % pkgname
    Log.out(output)
    return pkgname


def openApkGPInBrowser(args):
    """
    通过浏览器打开googleplay上的详情页面
    """
    pkgname = get_package_name(args)
    import webbrowser
    webbrowser.open(
        "https://play.google.com/store/apps/details?id=%s" % pkgname)


def check_apk_process(args):
    device = get_select_devices()
    if device != None and len(device) > 0:
        user_id = None
        pkgname = get_package_name(args)
        cmd = [Common.ADB, "-s", device, "shell", "ps"]
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
        execret = result.stdout.readlines()
        for item in execret:
            item = str(item, "utf-8")
            item_list = item.split()
            if pkgname in item_list:
                user_id = item_list[0]
        if user_id != None and user_id.strip() != "":
            global dump_process
            dump_process = True
            print()
            thread = Thread(target=start_process_check, args=(device, user_id))
            thread.daemon = True
            thread.start()
            while True:
                exit_flag = input()
                if exit_flag == 'e' or exit_flag == "E":
                    dump_process = False
                    break;
            thread.join()
        else:
            Log.out("[Logging...] 应用包未执行")
    elif device == None:
        Log.out("[Logging...] 没有发现设备")
        time.sleep(2)
        return
dump_process = False
def start_process_check(device, user_id):
    cmd = [Common.ADB, "-s", device, "shell", "ps", "|", "grep", user_id]
    while dump_process:
        subprocess.call(cmd)
        print()
        time.sleep(1)

def calc_maxlen():
    """计算每一行文字长度"""
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
    output = " 最小版本 | %s " % apk_info["min_version"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 目标版本 | %s " % apk_info["target_version"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 文件大小 | %s " % apk_info["apk_size"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名摘要 | %s" % apk_info["sign_md5"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名哈希 | %s" % apk_info["sign_sha1"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名哈希 | %s" % apk_info["sign_sha256"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 签名详情 | %s" % apk_info["sign_detail"]
    Log.out(output)

    if apk_info["sign_file"] != None and len(apk_info["sign_file"]) > 0:
        Log.out("-" * dash_len)
        output = " 签名文件 | %s" % apk_info["sign_file"]
        Log.out(output)

    #Log.out("-" * dash_len)
    #output = " 内部摘要 | %s" % apk_info["classes_md5"]
    # Log.out(output)

    Log.out("-" * dash_len)
    output = " 文件摘要 | %s" % apk_info["apk_md5"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 文件哈希 | %s" % apk_info["apk_sha1"]
    Log.out(output)

    Log.out("-" * dash_len)
    output = " 文件哈希 | %s" % apk_info["apk_sha256"]
    Log.out(output)
    Log.out("-" * dash_len)


# start ============================================================================================
if (len(sys.argv) < 2):
    Log.out("[Logging...] 脚本缺少参数 : %s <src_apk> 输出APK文件信息" %
            os.path.basename(sys.argv[0]), True)
    sys.exit()

try:
    opts, args = getopt.getopt(sys.argv[1:], "pmsiaxgu")
    for op, value in opts:
        if (op == "-m"):
            FILE_MD5 = True
        elif (op == "-s"):
            STR_MD5 = True
        elif (op == "-p"):
            APK_INFO = True
        elif (op == "-i"):
            INSTALL_APK = True
        elif (op == "-x"):
            INSTALL_XAPK = True
        elif (op == "-a"):
            AXMLPRINTER = True
        elif (op == "-g"):
            OPEN_IN_GP = True
        elif op == '-u':
            CHECK_PROCESS = True
except getopt.GetoptError as err:
    Log.out(err)
    sys.exit()

# 求字符串的MD5值
if STR_MD5 == True:
    string_md5(args)
    sys.exit()

check_arg(args)
# 安装apk
if INSTALL_APK == True:
    install_apk(args)
    sys.exit()
# 安装apk
if INSTALL_XAPK == True:
    install_xapk(args)
    sys.exit()
# 打印Android xml 文件
if AXMLPRINTER == True:
    print_xml(args)
    sys.exit()

if FILE_MD5 == True:
    processFileMd5(args)
    max_len = calc_maxlen()
    dash_len = 13 + max_len
    Log.out("-" * dash_len)
    output = " 文件名称 | %s" % apk_info["apk_file"]
    Log.out(output)
    Log.out("-" * dash_len)
    output = " 文件摘要 | %s" % apk_info["apk_md5"]
    output += "\n"
    output += " 文件哈希 | %s" % apk_info["apk_sha1"]
    output += "\n"
    output += " 文件哈希 | %s" % apk_info["apk_sha256"]
    output += "\n"
    if apk_info.get('sign_md5') != None:
        output += "\n"
        output += ("-" * dash_len)
        output += "\n"
        output += " 签名摘要 | %s" % apk_info["sign_md5"]
    if apk_info.get('sign_sha1') != None:
        output += "\n"
        output += " 签名哈希 | %s" % apk_info["sign_sha1"]
    if apk_info.get('sign_sha256') != None:
        output += "\n"
        output += " 签名哈希 | %s" % apk_info["sign_sha256"]
    Log.out(output)
    Log.out("-" * dash_len)
elif APK_INFO == True:
    processapk(args, get_app_info)
    processapk(args, file_size)
    processapk(args, md5_signfile)
    processapk(args, file_md5)
    processapk(args, file_sh1)
    processapk(args, file_sh256)
    print_apkinfo()
    Log.out("")
elif OPEN_IN_GP == True:
    openApkGPInBrowser(args)
    sys.exit(0)
elif CHECK_PROCESS:
    check_apk_process(args)
Common.pause()
