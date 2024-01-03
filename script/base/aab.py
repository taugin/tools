#!/usr/bin/python
# coding: UTF-8
import re
import sys
import os
import time
from tkinter.constants import FALSE
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import Common
import Log
import Utils

import getopt
import subprocess
import platform
import zipfile

AAB2APKS = False
INSTALL_APKS = False
DEVICE_SPEC_FILE = None
UNIVERSAL = False
LOCAL_TESTING = False

def input_no(start, end):
    try:
        while True:
            i = input("请输入设备顺序 : ")
            if i != None and i.isdigit() and int(i) >= start and int(i) <= end:
                return i
    except:
        Log.out("")
    return 1

def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        Log.out("[Logging...] 操作完成，按任意键退出", True)
        msvcrt.getch()

def inputvalue(prompt, max) :
    while True:
        p = input(prompt)
        if (p.isdigit()):
            if (int(p) >= 1 and int(p) <= max):
                return p

def getaabpackagename(file):
    result = None
    try:
        cmdlist = []
        cmdlist.append("java")
        cmdlist.append("-jar")
        cmdlist.append(Common.BUNDLE_TOOL)
        cmdlist.append("dump")
        cmdlist.append("manifest")
        cmdlist.append("--bundle=%s" % file)
        cmdlist.append("--xpath=/manifest/@package")
        #Log.out("cmdlist : %s" % (" ".join(cmdlist)))
        p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)
        result = p.stdout.read()
        result = result.decode().strip()
    except:
        pass
    return result

def readkeystore(src_file):
    filedir = os.path.dirname(src_file)
    listfile = os.listdir(filedir)
    storefiles = []
    #Log.out(listfile)
    index = 0
    storeindex = 0
    for file in listfile:
        if(file.rfind(".keystore") != -1 or file.rfind(".jks") != -1):
            storefiles.append(file)
            storeindex+=1
        index+=1
    # 在工程目录下的keystore文件夹中寻找签名文件
    if (len(storefiles) <= 0):
        keystoredir = os.path.normpath(os.path.join(filedir, "..", "..", "..", "..", "..", "keystore"))
        if os.path.exists(keystoredir):
            listfile = os.listdir(keystoredir)
            index = 0
            storeindex = 0
            for file in listfile:
                if(file.rfind(".keystore") != -1 or file.rfind(".jks") != -1):
                    storefiles.append(os.path.join(keystoredir, file))
                    storeindex+=1
                index+=1
    ##############################################
    if (len(storefiles) <= 0):
        packagename = getaabpackagename(src_file)
        if (packagename != None and len(packagename) > 0):
            pkg_storefile = os.path.join(Common.KEYSTORES_DIR, "appsignfiles", packagename)
            if (pkg_storefile != None and os.path.isdir(pkg_storefile)):
                Log.out("[Logging...] 文件包名 : [%s]" % packagename)
                listfile=os.listdir(pkg_storefile)
                #Log.out(listfile)
                index = 0
                storeindex = 0
                for file in listfile:
                    if(file.endswith(".keystore") or file.endswith(".jks")):
                        storefiles.append(os.path.join(pkg_storefile, file))
                        storeindex+=1
                    index+=1
    ##############################################
    if (storeindex > 1):
        index = 1
        for keyfile in storefiles:
            Log.out("             [%d] : %s" %(index, keyfile), True)
            index += 1
        p = inputvalue("[Logging...] 输入索引 : ", storeindex)
    else:
        p = 0
    if (storeindex <= 0):
        Log.out("[Logging...] 读取签名 : 找不到签名文件, 使用默认签名文件", True)
        keystorefile = os.path.normpath(Common.KEYSTORES_DEFAULT_FILE)
    else:
        keystorefile = storefiles[int(p) - 1]
    Log.out("[Logging...] 签名文件 : %s" % keystorefile, True)
    keystorename = os.path.basename(keystorefile)
    index = keystorename.rfind(".keystore")
    if index < 0:
        index = keystorename.rfind(".jks")
    filename = keystorename[0:index]
    splits = filename.split("_")
    if (len(splits) < 3):
        Log.out("[Logging...] 无法获取签名文件信息,请重命名签名文件格式 <[alias]_[storepass]_[aliaspass].keystore/jks>", True)
        sys.exit()
    keystorealias = splits[0]
    if (splits[1] != "pwd"):
        keystorepass = splits[1]
    else:
        keystorepass = splits[2]
    keyaliaspass = splits[2]

    if (keystorealias == "" or keystorepass == ""):
        Log.out("[Logging...] keystorealias or keystorepass is empty")
        sys.exit()

    keystorepath = os.path.normpath(os.path.join(filedir, keystorefile))
    retcode = subprocess.call([Common.KEYTOOL, "-list", "-keystore", keystorepath, "-storepass", keystorepass], stdout=subprocess.PIPE)
    if (retcode != 0):
        Log.out("[Logging...] 签名文件不正确", True)
        pause()
        sys.exit()
    keystoreinfo = []
    keystoreinfo.append(keystorepath)
    keystoreinfo.append(keystorepass)
    keystoreinfo.append(keystorealias)
    keystoreinfo.append(keyaliaspass)
    return keystoreinfo
    
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

def get_select_devices(wait_devices):
    if (wait_devices):
        wait_usb_devices()
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
            Log.out("\n发现的设备列表 : ")
            for index in range(0, len(devices)):
                Log.out("%s : %s" % (index + 1, devices[index][1]))
            
            if (len(devices) > 1):
                no = input_no(1, len(devices))
            else:
                no = 1
                Log.out("")
            return devices[int(no) - 1][0]
    except:
        pass
    return None

def transformAabForDevice():
    result = input("[Logging...] 设备转换 : [AAB -> APKS](Y/N) ")
    if result == "Y" or result == "y":
        return True
    return False

def aab2apks(aab_file):
    keystoreinfo = readkeystore(aab_file)
    basename, ext = os.path.splitext(aab_file)
    apks_file = "%s.apks" % basename
    cmdlist = []
    cmdlist.append("java")
    cmdlist.append("-jar")
    cmdlist.append(Common.BUNDLE_TOOL)
    cmdlist.append("build-apks")
    cmdlist.append("--bundle=%s" % aab_file)
    cmdlist.append("--output=%s" % apks_file)
    cmdlist.append("--overwrite")
    cmdlist.append("--verbose")
    cmdlist.append("--ks=%s" % keystoreinfo[0])
    cmdlist.append("--ks-pass=pass:%s" % keystoreinfo[1])
    cmdlist.append("--ks-key-alias=%s" % keystoreinfo[2])
    cmdlist.append("--key-pass=pass:%s" % keystoreinfo[3])
    select_device = None
    if UNIVERSAL != True:
        select_device = get_select_devices(False)
    if (select_device != None and transformAabForDevice()):
        Log.out("[Logging...] 连接设备 : [%s]\n" % select_device, True)
        cmdlist.append("--connected-device")
        cmdlist.append("--device-id=%s" % select_device)

    if (UNIVERSAL == True):
        cmdlist.append("--mode=universal")

    if (LOCAL_TESTING == True):
        cmdlist.append("--local-testing")

    if (DEVICE_SPEC_FILE != None and len(DEVICE_SPEC_FILE) > 0 and os.path.exists(DEVICE_SPEC_FILE)):
        cmdlist.append("--device-spec=%s" % DEVICE_SPEC_FILE)
    
    #Log.out("cmdlist : %s" % cmdlist)
    tmp_value = ""
    tmp_value += cmdlist[0] + " "
    tmp_value += cmdlist[1] + " "
    tmp_value += cmdlist[2] + " "
    Log.out("[Logging...] 开始转换 : %s" % tmp_value, True)
    for index in range(0, len(cmdlist)):
        if (index >= 3):
            Log.out("\t\t\t\t" + cmdlist[index])
    Log.out("")
    start_time = time.time()
    retcode = subprocess.call(cmdlist)
    end_time = time.time()
    if (retcode == 0):
        Log.out("[Logging...] 转换成功 : [%s -> %s]" % (aab_file, apks_file), True)
        exp_time = end_time - start_time
        Log.out("[Logging...] 转换耗时 : [%.2fs]" % exp_time, True)
        #time.sleep(3)
        if UNIVERSAL == True and os.path.exists(apks_file):
            extractApksInUniversalMode(apks_file, basename)
        pause()
    else:
        Log.out("[Logging...] 转换失败", True)
        pause()
    pass

def extractApksInUniversalMode(apks_file, basename):
    final_apk_name = "%s.apk" % basename
    cur_dir = os.path.dirname(apks_file)
    universal_path = os.path.join(cur_dir, "universal.apk")
    if (os.path.exists(universal_path)):
        os.remove(universal_path)
    if (os.path.exists(final_apk_name)):
        os.remove(final_apk_name)
    Log.out("[Logging...] 解压文件 : [%s -> %s]" % (apks_file, final_apk_name), True)
    apks_zip_file = zipfile.ZipFile(apks_file, "r")
    apks_zip_file.extract("universal.apk", ".")
    apks_zip_file.close()
    os.rename(universal_path, final_apk_name)
    if (os.path.exists(apks_file)):
        os.remove(apks_file)

def install_apks(apks_file):
    select_device = get_select_devices(True)
    cmdlist = []
    cmdlist.append("java")
    cmdlist.append("-jar")
    cmdlist.append(Common.BUNDLE_TOOL)
    cmdlist.append("install-apks")
    cmdlist.append("--allow-test-only")
    cmdlist.append("--allow-downgrade")
    cmdlist.append("--apks=%s" % apks_file)
    if (select_device != None):
        cmdlist.append("--device-id=%s" % select_device)
    tmp_value = ""
    tmp_value += cmdlist[0] + " "
    tmp_value += cmdlist[1] + " "
    tmp_value += cmdlist[2]
    Log.out("[Logging...] 开始安装 : %s" % tmp_value, True)
    for index in range(0, len(cmdlist)):
        if (index >= 3):
            Log.out("\t\t\t\t" + cmdlist[index])
    retcode = subprocess.call(cmdlist)
    if (retcode == 0):
        Log.out("[Logging...] 安装成功 : [%s]" % (apks_file), True)
        time.sleep(2)
    else:
        Log.out("[Logging...] 安装失败", True)
        pause()
if (len(sys.argv) < 2):
    Log.out("[Logging...] 脚本缺少参数 : %s <src_apk> 输出APK文件信息" % os.path.basename(sys.argv[0]), True);
    sys.exit()

try:
    opts, args = getopt.getopt(sys.argv[1:], "tiuls:")
    for op, value in opts:
        if (op == "-t"):
            AAB2APKS = True
        elif (op == "-i") :
            INSTALL_APKS = True
        elif (op == "-u"):
            UNIVERSAL = True
        elif (op == "-l"):
            LOCAL_TESTING = True
        elif (op == "-s"):
            DEVICE_SPEC_FILE = value

except getopt.GetoptError as err:
    Log.out(err)
    sys.exit()

if (AAB2APKS == True):
    aab2apks(os.path.abspath(args[0]))
    sys.exit(0)
if (INSTALL_APKS):
    install_apks(os.path.abspath(args[0]))