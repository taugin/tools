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

def get_lib_dirs(mergedapk):
    mergedzip = zipfile.ZipFile(mergedapk, "r")
    liblist = []
    for name in mergedzip.namelist():
        if (name.startswith("lib")):
            dirname = os.path.dirname(name)
            if (dirname not in liblist):
                liblist += [dirname]
    return liblist

def should_copypayapklibfile(name, liblist):
    if (liblist == None or len(liblist) <= 0):
        return True
    dirname = os.path.dirname(name)
    if (dirname.startswith("lib") and dirname not in liblist):
        return False
    return True

#从支付apk中拷贝文件
def copy_payapk(mergedapk, payapk):
    Log.out("[Logging...] 拷贝支付文件", True)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    liblist = get_lib_dirs(mergedapk)
    payzip = zipfile.ZipFile(payapk, "r")
    for name in payzip.namelist():
        should_copy = should_copypayapkfile(name)
        should_copy_lib = should_copypayapklibfile(name, liblist)
        exists_in = exists_in_gameapk(mergedzip, name)
        if (should_copy and should_copy_lib and exists_in == False):
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

def exists_in_gameapk(zip, name):
    try:
        zipinfo = zip.getinfo(name)
        return zipinfo != None
    except:
        return False

#从游戏apk中拷贝文件
def copy_gameapk(mergedapk, gameapk):
    Log.out("[Logging...] 拷贝游戏文件", True)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    gamezip = zipfile.ZipFile(gameapk, "r")
    for name in gamezip.namelist():
        shouldcopy = should_copygameapkfile(name)
        exists_in = exists_in_gameapk(mergedzip, name)
        if (shouldcopy == True and exists_in == False):
            mergedzip.writestr(name, gamezip.read(name), zipfile.ZIP_DEFLATED)
    mergedzip.close()
    gamezip.close()

#将支付apk中的classes.dex文件，压缩成Common.PAY_STUBDATA，并且放置到合并的apk
#的assets文件夹内
def generate_pay(mergedapk, payapk):
    payzip = zipfile.ZipFile(payapk, "r")
    tmpzipfile = "tmp.apk"
    tmpzip = zipfile.ZipFile(tmpzipfile, "w")
    tmpzip.writestr("classes.dex", payzip.read("classes.dex"), zipfile.ZIP_DEFLATED)
    payzip.close()
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

#添加公司信息到合并的apk中的assets文件内
def add_company_info(mergedapk, company_name):
    if (company_name == None or company_name == ""):
        return
    Log.out("[Logging...] 配置公司名称 : [%s]" % company_name, True)
    subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.COMPANYFILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    doc = Document()  #创建DOM文档对象
    root = doc.createElement('resources') #创建根元素
    doc.appendChild(root)
    gbstring = doc.createElement("partner_name")
    textnode = doc.createTextNode(company_name)
    gbstring.appendChild(textnode)
    root.appendChild(gbstring)
    gbstringfile = "ccp_strings.xml"
    f = open(gbstringfile,'wb')
    f.write(doc.toxml(encoding = "utf-8"))
    f.close()
    tree = ET.parse(gbstringfile)
    indent(tree.getroot())
    tree.write(gbstringfile, encoding="utf-8", xml_declaration=True)
    mergedzip.write(gbstringfile, Common.COMPANYFILE, zipfile.ZIP_DEFLATED)
    mergedzip.close()
    if (os.path.exists(gbstringfile)):
        os.remove(gbstringfile)

def copy_fromapk(mergedapk, gameapk, payapk, company_name):
    if (os.path.exists(mergedapk) == False):
        Log.out("[Error...] 无法定位文件 %s" % mergedapk, True)
        sys.exit(0)
    if (os.path.exists(gameapk) == False):
        Log.out("[Error...] 无法定位文件 %s" % gameapk, True)
        sys.exit(0)
    if (os.path.exists(payapk) == False):
        Log.out("[Error...] 无法定位文件 %s" % payapk, True)
        sys.exit(0)

    subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.PLUGIN_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.ITEM_MAPPER], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([Common.AAPT_BIN, "r", mergedapk, Common.PAY_STUBDATA], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    copy_gameapk(mergedapk, gameapk)
    copy_payapk(mergedapk, payapk)
    generate_pay(mergedapk, payapk)

    add_company_info(mergedapk, company_name)
    Log.out("[Logging...] 文件拷贝完成\n", True)
    return True

if __name__ == "__main__":
    copy_fromapk(sys.argv[1], sys.argv[2], sys.argv[3])