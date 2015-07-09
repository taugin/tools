#!/usr/bin/python
# coding: UTF-8

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

RE_STRING = "PACKAGE_NAME_ABC"
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"
COCOSPAY_ACTIVITY = "com.cocospay.CocosPayActivity"
COCOSPAYACTIVITY_ENTRY_NAME = "dest_activity"

UNICOM_ACTIVITY = "com.unicom.dcLoader.welcomeview"
UNICOMPAYACTIVITY_ENTRY_NAME = "UNICOM_DIST_ACTIVITY"

MAIN_ACTIVITY_XPATH = ".//action/[@{%s}name='android.intent.action.MAIN']/../category/[@{%s}name='android.intent.category.LAUNCHER']/../.." % (XML_NAMESPACE, XML_NAMESPACE)
CATEGORY_XPATH = ".//action/[@{%s}name='android.intent.action.MAIN']/../category/[@{%s}name='android.intent.category.LAUNCHER']/.." % (XML_NAMESPACE, XML_NAMESPACE)

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


def remove_dup_permission(gameroot):
    log("[Logging...] 去除重复权限", True)
    permissions = gameroot.findall(".//uses-permission")
    list = []
    if (permissions != None):
        for item in permissions:
            permisson_name = item.attrib["{%s}name" % XML_NAMESPACE]
            if (permisson_name in list):
                gameroot.remove(item)
            else:
                list += [permisson_name]

def add_entry_activity(gameroot):
    log("[Logging...] 设置程序入口", True)
    mainactivity = gameroot.findall(MAIN_ACTIVITY_XPATH)
    if (mainactivity == None or len(mainactivity) <= 0):
        return

    entry_activity = None
    screenOritation = None
    old_entry_class = None
    for activity in mainactivity:
        activityname = activity.attrib["{%s}name" % XML_NAMESPACE]
        if (activityname == COCOSPAY_ACTIVITY):
            entry_activity = activity
            mainactivity.remove(activity)
        else:
            screenOritation = activity.get("{%s}screenOrientation" % XML_NAMESPACE)
            old_entry_class = activity.attrib["{%s}name" % XML_NAMESPACE]
            launcher_filter = activity.find(CATEGORY_XPATH)
            category = launcher_filter.find(".//category")
            launcher_filter.remove(category)

    if (entry_activity != None):
        if (screenOritation != None):
            entry_activity.set("{%s}screenOrientation" % XML_NAMESPACE, screenOritation)
        dest_activity = entry_activity.find("meta-data[@{%s}name='%s']" % (XML_NAMESPACE, COCOSPAYACTIVITY_ENTRY_NAME))
        if (old_entry_class != None):
            if (dest_activity != None):
                dest_activity.set("{%s}value" % XML_NAMESPACE, old_entry_class)
            else:
                element = ET.Element("meta-data")
                element.attrib["{%s}name" % XML_NAMESPACE] = "dest_activity"
                element.attrib["{%s}value" % XML_NAMESPACE] = old_entry_class
                entry_activity.append(element)


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

def modify_unicom_metadata(gameroot):
    cocospaymetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (XML_NAMESPACE, COCOSPAY_ACTIVITY, XML_NAMESPACE, COCOSPAYACTIVITY_ENTRY_NAME))
    if (cocospaymetadata == None):
        return
    unicommetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (XML_NAMESPACE, UNICOM_ACTIVITY, XML_NAMESPACE, UNICOMPAYACTIVITY_ENTRY_NAME))
    if (unicommetadata != None):
        value = cocospaymetadata.attrib["{%s}value" % XML_NAMESPACE]
        if (value != None):
            log("[Logging...] 添加联通入口 : [%s]" % value, True)
            unicommetadata.set("{%s}value" % XML_NAMESPACE, value)

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

    #修改联通
    modify_unicom_metadata(gameroot)
    #去除重复的权限
    remove_dup_permission(gameroot)
    add_entry_activity(gameroot)
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