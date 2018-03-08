#!/usr/bin/python
# coding: UTF-8

'''
从支付apk和游戏apk中拷贝必要的文件到
已经合并的apk
'''
import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Common
import Log

import shutil
import zipfile
import platform
import subprocess
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document

def should_copyslaveapkfile(name):
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

def get_lib_dirs(mergedapk):
    mergedzip = zipfile.ZipFile(mergedapk, "r")
    liblist = []
    for name in mergedzip.namelist():
        if (name.startswith("lib")):
            dirname = os.path.dirname(name)
            if (dirname not in liblist):
                liblist += [dirname]
    return liblist

def should_copyslaveapklibfile(name, liblist):
    if (liblist == None or len(liblist) <= 0):
        return True
    dirname = os.path.dirname(name)
    if (dirname.startswith("lib") and dirname not in liblist):
        return False
    return True

#从支付apk中拷贝文件
def copy_slaveapk(mergedapk, slaveapk):
    Log.out("[Logging...] 拷贝支付文件", True)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    liblist = get_lib_dirs(mergedapk)
    slavezip = zipfile.ZipFile(slaveapk, "r")
    for name in slavezip.namelist():
        should_copy = should_copyslaveapkfile(name)
        should_copy_lib = should_copyslaveapklibfile(name, liblist)
        exists_in = exists_in_masterapk(mergedzip, name)
        if (should_copy and should_copy_lib and exists_in == False):
            mergedzip.writestr(name, slavezip.read(name))
    mergedzip.close()
    slavezip.close()

def should_copymasterapkfile(name):
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

def exists_in_masterapk(zip, name):
    try:
        zipinfo = zip.getinfo(name)
        return zipinfo != None
    except:
        return False

#从游戏apk中拷贝文件
def copy_masterapk(mergedapk, masterapk):
    Log.out("[Logging...] 拷贝游戏文件", True)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    masterzip = zipfile.ZipFile(masterapk, "r")
    for name in masterzip.namelist():
        shouldcopy = should_copymasterapkfile(name)
        exists_in = exists_in_masterapk(mergedzip, name)
        if (shouldcopy == True and exists_in == False):
            mergedzip.writestr(name, masterzip.read(name), zipfile.ZIP_DEFLATED)
    mergedzip.close()
    masterzip.close()

#将支付apk中的classes.dex文件，压缩成Common.PAY_STUBDATA，并且放置到合并的apk
#的assets文件夹内
def generate_slave(mergedapk, slaveapk):
    slavezip = zipfile.ZipFile(slaveapk, "r")
    tmpzipfile = "tmp.apk"
    tmpzip = zipfile.ZipFile(tmpzipfile, "w")
    tmpzip.writestr("classes.dex", slavezip.read("classes.dex"), zipfile.ZIP_DEFLATED)
    slavezip.close()
    tmpzip.close()
    
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    mergedzip.write(tmpzipfile, Common.PAY_STUBDATA, zipfile.ZIP_DEFLATED)
    mergedzip.close()
    if (os.path.exists(tmpzipfile)):
        os.remove(tmpzipfile)

## Get pretty look
#美化xml文件
def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem

def copy_fromapk(mergedapk, masterapk, slaveapk, company_name):
    if (os.path.exists(mergedapk) == False):
        Log.out("[Logging...] 无法定位文件 %s" % mergedapk, True)
        sys.exit(0)
    if (os.path.exists(masterapk) == False):
        Log.out("[Logging...] 无法定位文件 %s" % masterapk, True)
        sys.exit(0)
    if (os.path.exists(slaveapk) == False):
        Log.out("[Logging...] 无法定位文件 %s" % slaveapk, True)
        sys.exit(0)

    subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.PLUGIN_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.ITEM_MAPPER], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.PAY_STUBDATA], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    copy_masterapk(mergedapk, masterapk)
    copy_slaveapk(mergedapk, slaveapk)

    Log.out("[Logging...] 文件拷贝完成\n", True)
    return True

if __name__ == "__main__":
    copy_fromapk(sys.argv[1], sys.argv[2], sys.argv[3])