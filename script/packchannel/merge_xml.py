#!/usr/bin/python
# coding: UTF-8

import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Common
import Log

import re
import subprocess
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

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

def key_component_check(gameroot):
    pay_activity = gameroot.find(".//activity/[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_ACTIVITY))
    if (pay_activity == None):
        Log.out("[Eroring...] 缺失重要组件 : [%s]" % Common.PAY_ACTIVITY, True)
    pay_service = gameroot.find(".//service/[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_SERVICE))
    if (pay_service == None):
        Log.out("[Eroring...] 缺失重要组件 : [%s]" % Common.PAY_SERVICE, True)

#去除重复权限
def remove_dup_permission(gameroot):
    Log.out("[Logging...] 去除重复权限", True)
    permissions = gameroot.findall(".//uses-permission")
    list = []
    if (permissions != None):
        for item in permissions:
            permisson_name = item.attrib["{%s}name" % Common.XML_NAMESPACE]
            if (permisson_name in list):
                gameroot.remove(item)
            else:
                list += [permisson_name]

#去除敏感权限
def remove_sensitive_permission(gameroot):
    Log.out("[Logging...] 去除敏感权限", True)
    list = config_parser.get_sensitive_permissions()
    if (list == None or len(list) <= 0):
        return
    permissions = gameroot.findall(".//uses-permission")
    if (permissions != None):
        for item in permissions:
            permisson_name = item.attrib["{%s}name" % Common.XML_NAMESPACE]
            if (permisson_name in list):
                Log.out("[Logging...] 敏感权限名称 : [%s]" % permisson_name, True)
                gameroot.remove(item)

def add_entry_activity(gameroot):
    mainactivity = gameroot.findall(Common.MAIN_ACTIVITY_XPATH)
    if (mainactivity == None or len(mainactivity) <= 0):
        return

    entry_activity = None
    old_entry_class = None
    for activity in mainactivity:
        activityname = activity.attrib["{%s}name" % Common.XML_NAMESPACE]
        if (activityname == Common.PAY_ACTIVITY):
            entry_activity = activity
            mainactivity.remove(activity)
        else:
            old_entry_class = activity.attrib["{%s}name" % Common.XML_NAMESPACE]
            launcher_filter = activity.find(Common.CATEGORY_XPATH)
            category = launcher_filter.find(".//category")
            launcher_filter.remove(category)

    #设置游戏真正入口Activity
    if (entry_activity != None):
        #查找meta-data
        dest_activity = entry_activity.find("meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAYACTIVITY_ENTRY_NAME))
        if (old_entry_class != None):
            Log.out("[Logging...] 设置程序入口 : [%s]" % old_entry_class, True)
            if (dest_activity != None):
                dest_activity.set("{%s}value" % Common.XML_NAMESPACE, old_entry_class)
            else:
                element = ET.Element("meta-data")
                element.attrib["{%s}name" % Common.XML_NAMESPACE] = "dest_activity"
                element.attrib["{%s}value" % Common.XML_NAMESPACE] = old_entry_class
                entry_activity.append(element)

    #设置程序入口Activity属性值
    if (entry_activity != None):
        dest_activity = entry_activity.find("meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAYACTIVITY_ENTRY_NAME))
        if (dest_activity == None):
            return
        entry_activity_class = dest_activity.get("{%s}value" % Common.XML_NAMESPACE)
        if (entry_activity_class == None or entry_activity_class == ""):
            return

        #设置程序入口屏幕方向
        real_entry_activity = gameroot.find(".//activity[@{%s}name='%s']" % (Common.XML_NAMESPACE, entry_activity_class))
        if (real_entry_activity != None):
            screenOritation = real_entry_activity.get("{%s}screenOrientation" % Common.XML_NAMESPACE)
            if (screenOritation == None):
                return
            entry_activity.set("{%s}screenOrientation" % Common.XML_NAMESPACE, screenOritation)
            set_orientation(gameroot, screenOritation)

def set_orientation(gameroot, screenOritation):
    if (screenOritation == None):
        return
    activity_class = "cn.cmgame.billing.api.GameOpenActivity"
    activity = gameroot.find(".//activity[@{%s}name='%s']" % (Common.XML_NAMESPACE, activity_class))
    if (activity != None):
        Log.out("[Logging...] 基地屏幕方向 : [%s]" % screenOritation, True)
        activity.set("{%s}screenOrientation" % Common.XML_NAMESPACE, screenOritation)

    activity_class = "com.unicom.dcLoader.welcomeview"
    activity = gameroot.find(".//activity[@{%s}name='%s']" % (Common.XML_NAMESPACE, activity_class))
    if (activity != None):
        Log.out("[Logging...] 联通屏幕方向 : [%s]" % screenOritation, True)
        activity.set("{%s}screenOrientation" % Common.XML_NAMESPACE, screenOritation)

def modify_pay_action(rc, pkgname):
    Log.out("[Logging...] 替换真实包名 : [%s] --> [%s]" % (Common.RE_STRING, pkgname), True)
    strinfo = re.compile(Common.RE_STRING)
    rc = strinfo.sub(pkgname, rc)
    return rc

def modify_pkgname(rc, pkgname, newpkgname):
    if (newpkgname != None and newpkgname != ""):
        Log.out("[Logging...] 使用配置包名 : [%s]" % newpkgname, True)
        strinfo = re.compile(pkgname)
        rc = strinfo.sub(newpkgname, rc)
    return rc

def modify_unicom_metadata(gameroot):
    paymetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_ACTIVITY, Common.XML_NAMESPACE, Common.PAYACTIVITY_ENTRY_NAME))
    if (paymetadata == None):
        return
    unicommetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.UNICOM_ACTIVITY, Common.XML_NAMESPACE, Common.UNICOMPAYACTIVITY_ENTRY_NAME))
    if (unicommetadata != None):
        value = paymetadata.attrib["{%s}value" % Common.XML_NAMESPACE]
        if (value != None):
            Log.out("[Logging...] 添加联通入口 : [%s]" % value, True)
            unicommetadata.set("{%s}value" % Common.XML_NAMESPACE, value)

###############################################################################
#合并AndroidManifest.xml文件
def merge_androidmanifest(decompiledfoler, sdkfolder):
    Log.out("[Logging...] 正在合并文件 : [AndroidManifest.xml]", True)
    if (os.path.exists(decompiledfoler) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % decompiledfoler, True)
        return False
    if (os.path.exists(sdkfolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % sdkfolder, True)
        return False
    gamemanifest = "%s/AndroidManifest.xml" % decompiledfoler;
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

    indent(gameroot)
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
        indent(root)
        tree.write(gamemanifest, encoding='utf-8', xml_declaration=True)
###############################################################################
if __name__ == "__main__":
    merge_xml(sys.argv[1], sys.argv[2])