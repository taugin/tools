#!/usr/bin/python
# coding: UTF-8
#引入别的文件夹的模块

import moduleconfig
import Common
import Log
import Utils


import os
import xml.etree.ElementTree as ET
#from xml.etree import cElementTree as ET
#from xml.dom import minidom

###############################################################################
#合并AndroidManifest.xml文件
def merge_manifest(decompiledfolder, sdkfolder):
    Log.out("[Logging...] 正在合并文件 : [AndroidManifest.xml]", True)
    if (os.path.exists(decompiledfolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % decompiledfolder, True)
        return False
    if (os.path.exists(sdkfolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % sdkfolder, True)
        return False
    gamemanifest = "%s/AndroidManifest.xml" % decompiledfolder;
    paymanifest = "%s/AndroidManifest.xml" % sdkfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    gametree = ET.parse(gamemanifest)
    gameroot = gametree.getroot()
    gameapplication = gameroot.find("application")

    paytree = ET.parse(paymanifest)
    payroot = paytree.getroot()
    payapplication = payroot.find("application")

    for item in payroot.getchildren():
        if (item.tag == "uses-permission"):
            gameroot.append(item)

    for item in payapplication.getchildren():
        gameapplication.append(item)

    Utils.indent(gameroot)
    gametree.write(gamemanifest, encoding='utf-8', xml_declaration=True)
    Log.out("[Logging...] 文件合并完成\n", True)
    return True

#修改AndroidManifest.xml包名
def modify_package(decompiledfolder, pkg_suffix):
    if (pkg_suffix == None or pkg_suffix == ""):
        return
    gamemanifest = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    tree = ET.parse(gamemanifest)
    root = tree.getroot()
    oldpkg = root.get("package")
    if (oldpkg != None and oldpkg != ""):
        newpkg = oldpkg + pkg_suffix
        Log.out("[Logging...] 修改配置包名 : [%s]" % newpkg, True)
        root.set("package", newpkg)
        Utils.indent(root)
        tree.write(gamemanifest, encoding='utf-8', xml_declaration=True)
###############################################################################