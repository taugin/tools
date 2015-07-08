#!/usr/bin/python
# coding: UTF-8

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

RE_STRING = "PACKAGE_NAME"
RE_STRING = "XXX"
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

def log(str, show=False):
    if (show):
        print(str)

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

def merge_xml(gamefolder, payfolder):
    merge_xml_change_pkg(gamefolder, payfolder, None)

def modify_pay_action(rc, pkgname):
    log("[Logging...] 替换真实包名 : [%s] --> [%s]" % (RE_STRING, pkgname), True)
    strinfo = re.compile(RE_STRING)
    rc = strinfo.sub(pkgname, rc)
    return rc

def modify_pkgname(rc, pkgname, newpkgname):
    if (newpkgname != None and newpkgname != ""):
        log("[Logging...] 使用配置包名 : [%s]" % newpkgname, True)
        strinfo = re.compile(pkgname)
        rc = strinfo.sub(newpkgname, rc)
    return rc

def merge_xml_change_pkg(gamefolder, payfolder, newpkgname):
    log("[Logging...] 正在合并文件 : [AndroidManifest.xml]", True)
    if (os.path.exists(gamefolder) == False):
        log("[Error...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        log("[Error...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    gamemanifest = "%s/AndroidManifest.xml" % gamefolder;
    paymanifest = "%s/AndroidManifest.xml" % payfolder;
    ET.register_namespace('android', XML_NAMESPACE)
    gametree = ET.parse(gamemanifest)
    gameroot = gametree.getroot()
    gameapplication = gameroot.find("application")
    pkgname = gameroot.get("package")

    paytree = ET.parse(paymanifest)
    payroot = paytree.getroot()
    payapplication = payroot.find("application")

    for item in payroot.getchildren():
        if (item.tag == "uses-permission"):
            gameroot.append(item)

    for item in payapplication.getchildren():
        gameapplication.append(item)

    indent(gameroot)
    gametree.write(gamemanifest, encoding='utf-8', xml_declaration=True)

    f = open(gamemanifest, "r")
    rc = f.read()

    #修改pay action
    rc = modify_pay_action(rc, pkgname)
    #修改包名
    rc = modify_pkgname(rc, pkgname, newpkgname)

    f.close()
    f = open(gamemanifest, "w")
    f.write(rc)
    f.close()
    log("[Logging...] 文件合并完成\n", True)
    return True

if __name__ == "__main__":
    merge_xml(sys.argv[1], sys.argv[2])