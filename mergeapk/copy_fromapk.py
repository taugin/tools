#!/usr/bin/python
# coding: UTF-8

import os
import sys
import shutil
import zipfile
import platform
import subprocess
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document

PLUGIN_FILE = "assets/plugins.xml"
ITEM_MAPPER = "assets/ItemMapper.xml"
#COCOSPAYAPK = "assets/CocosPaySdk.apk"
COCOSPAYAPK = "assets/com.cocospay.stub.dat"


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

def copy_payapk(mergedapk, payapk):
    log("[Logging...] 拷贝支付文件", True)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    liblist = get_lib_dirs(mergedapk)
    payzip = zipfile.ZipFile(payapk, "r")
    for name in payzip.namelist():
        if (should_copypayapkfile(name) and should_copypayapklibfile(name, liblist)):
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

def copy_gameapk(mergedapk, gameapk):
    log("[Logging...] 拷贝游戏文件", True)
    mergedzip = zipfile.ZipFile(mergedapk, "a")
    gamezip = zipfile.ZipFile(gameapk, "r")
    for name in gamezip.namelist():
        shouldcopy = should_copygameapkfile(name)
        exists_in = exists_in_gameapk(mergedzip, name)
        if (shouldcopy == True and exists_in == False):
            mergedzip.writestr(name, gamezip.read(name), zipfile.ZIP_DEFLATED)
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

## Get pretty look
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

def add_company_info(mergedapk, company_name):
    if (company_name == None or company_name == ""):
        return
    log("[Logging...] 配置公司名称 : [%s]" % company_name, True)
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
    mergedzip.write(gbstringfile, "assets/%s" % gbstringfile, zipfile.ZIP_DEFLATED)
    mergedzip.close()
    if (os.path.exists(gbstringfile)):
        os.remove(gbstringfile)

def copy_fromapk(mergedapk, gameapk, payapk, company_name):
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
    add_company_info(mergedapk, company_name)
    log("[Logging...] 文件拷贝完成\n", True)
    return True

if __name__ == "__main__":
    copy_fromapk(sys.argv[1], sys.argv[2], sys.argv[3])