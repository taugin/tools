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
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

def log(str, show=False):
    if (show):
        print(str)

def merge_xml(gamefolder, payfolder):
    log("[Logging...] 正在合并AndroidManifest.xml文件", True)
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

    gametree.write(gamemanifest)
    f = open(gamemanifest, "r")
    strinfo = re.compile(RE_STRING)
    rc = strinfo.sub(pkgname, f.read())
    f.close()
    f = open(gamemanifest, "w")
    f.write(rc)
    f.close()
    log("[Logging...] AndroidManifest.xml文件合并完成\n", True)
    return True

if __name__ == "__main__":
    merge_xml(sys.argv[1], sys.argv[2])