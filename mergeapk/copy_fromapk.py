#!/usr/bin/python
# coding: UTF-8

import os
import sys
import shutil
import zipfile
import platform
import subprocess

PLUGIN_FILE = "assets/plugins.xml"
ITEM_MAPPER = "assets/ItemMapper.xml"
COCOSPAYAPK = "assets/CocosPaySdk.apk"

EXE = ""
if (platform.system().lower() == "windows"):
    EXE = ".exe"
AAPT = "aapt%s" % EXE
AAPT_FILE = os.path.join(os.path.dirname(sys.argv[0]), AAPT)

def log(str, show=True):
    if (show):
        print(str)

def should_copypayapkfile(name):
    if (name.startswith("res")):
        return False
    if (name.startswith("META-INF")):
        return False
    if (name.startswith("AndroidManifest.xml")):
        return False
    if (name.startswith("classes.dex")):
        return False
    if (name.startswith("resources.arsc")):
        return False
    return True

def copy_payapk(mergedapk, payapk):
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    payzip = zipfile.ZipFile(payapk, "r")
    for name in payzip.namelist():
        if (should_copypayapkfile(name)):
            mergedzip.writestr(name, payzip.read(name))
    mergedzip.close()
    payzip.close()

def should_copygameapkfile(name):
    if (name.startswith("assets")):
        return False
    if (name.startswith("lib")):
        return False
    if (name.startswith("res")):
        return False
    if (name.startswith("META-INF")):
        return False
    if (name.startswith("AndroidManifest.xml")):
        return False
    if (name.startswith("classes.dex")):
        return False
    if (name.startswith("resources.arsc")):
        return False
    return True

def copy_gameapk(mergedapk, gameapk):
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    gamezip = zipfile.ZipFile(gameapk, "r")
    for name in gamezip.namelist():
        if (should_copygameapkfile(name)):
            mergedzip.writestr(name, gamezip.read(name))
    mergedzip.close()
    gamezip.close()

def generate_cocospay(mergedapk, payapk):
    payzip = zipfile.ZipFile(payapk, "r")
    tmpzipfile = "tmp.apk"
    tmpzip = zipfile.ZipFile(tmpzipfile, "w")
    tmpzip.writestr("classes.dex", payzip.read("classes.dex"), zipfile.ZIP_DEFLATED)
    payzip.close()
    tmpzip.close()
    
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    mergedzip.write(tmpzipfile, COCOSPAYAPK, zipfile.ZIP_DEFLATED)
    mergedzip.close()
    if (os.path.exists(tmpzipfile)):
        os.remove(tmpzipfile)

def copy_fromapk(mergedapk, gameapk, payapk):
    log("[Logging...] 正在拷贝APK相关文件", True)
    if (os.path.exists(mergedapk) == False):
        log("[Error...] 无法定位文件 %s" % mergedapk, True)
        sys.exit(0)
    if (os.path.exists(gameapk) == False):
        log("[Error...] 无法定位文件 %s" % gameapk, True)
        sys.exit(0)
    if (os.path.exists(payapk) == False):
        log("[Error...] 无法定位文件 %s" % payapk, True)
        sys.exit(0)

    subprocess.call([AAPT_FILE, "r", mergedapk, PLUGIN_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([AAPT_FILE, "r", mergedapk, ITEM_MAPPER], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([AAPT_FILE, "r", mergedapk, COCOSPAYAPK], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    copy_gameapk(mergedapk, gameapk)
    copy_payapk(mergedapk, payapk)
    generate_cocospay(mergedapk, payapk)

    log("[Logging...] APK相关文件拷贝完成\n", True)
    return True

if __name__ == "__main__":
    copy_fromapk(sys.argv[1], sys.argv[2], sys.argv[3])