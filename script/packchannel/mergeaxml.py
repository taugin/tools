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
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    sdkmanifest = "%s/AndroidManifest.xml" % sdkfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    gametree = ET.parse(manifestfile)
    gameroot = gametree.getroot()
    gameapplication = gameroot.find("application")

    sdktree = ET.parse(sdkmanifest)
    sdkroot = sdktree.getroot()
    sdkapplication = sdkroot.find("application")

    for item in sdkroot.getchildren():
        if (item.tag == "uses-permission"):
            gameroot.append(item)

    for item in sdkapplication.getchildren():
        gameapplication.append(item)

    Utils.indent(gameroot)
    gametree.write(manifestfile, encoding='utf-8', xml_declaration=True)
    Log.out("[Logging...] 文件合并完成\n", True)
    return True

#修改AndroidManifest.xml包名
def modify_package(decompiledfolder, pkg_suffix):
    if (pkg_suffix == None or pkg_suffix == ""):
        return
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    tree = ET.parse(manifestfile)
    root = tree.getroot()
    oldpkg = root.get("package")
    if (oldpkg != None and oldpkg != ""):
        newpkg = oldpkg + pkg_suffix
        Log.out("[Logging...] 修改配置包名 : [%s]" % newpkg, True)
        root.set("package", newpkg)
        Utils.indent(root)
        tree.write(manifestfile, encoding='utf-8', xml_declaration=True)

#添加meta到Application标签下面
def add_meta(decompiledfolder, meta_data):
    if (len(meta_data) <= 0):
        return
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    tree = ET.parse(manifestfile)
    root = tree.getroot()
    application = root.find("application")
    for data in meta_data:
        element = ET.Element("meta-data")
        name = Utils.getvalue(data, "name")
        value = Utils.getvalue(data, "value")
        element.set("{%s}name" % Common.XML_NAMESPACE, name)
        element.set("{%s}value" % Common.XML_NAMESPACE, value)
        application.append(element)
        Log.out("[Logging...] 添加元始数据 : [%s] --> [%s]" % (name, value), True)
    Utils.indent(root)
    tree.write(manifestfile, encoding='utf-8', xml_declaration=True)
    Log.out("[Logging...] 添加据据完成\n")
###############################################################################