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
import config_parser

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
    cocospay_activity = gameroot.find(".//activity/[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_ACTIVITY))
    if (cocospay_activity == None):
        Log.out("[Eroring...] 缺失重要组件 : [%s]" % Common.PAY_ACTIVITY, True)
    cocospay_service = gameroot.find(".//service/[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_SERVICE))
    if (cocospay_service == None):
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
    cocospaymetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_ACTIVITY, Common.XML_NAMESPACE, Common.PAYACTIVITY_ENTRY_NAME))
    if (cocospaymetadata == None):
        return
    unicommetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.UNICOM_ACTIVITY, Common.XML_NAMESPACE, Common.UNICOMPAYACTIVITY_ENTRY_NAME))
    if (unicommetadata != None):
        value = cocospaymetadata.attrib["{%s}value" % Common.XML_NAMESPACE]
        if (value != None):
            Log.out("[Logging...] 添加联通入口 : [%s]" % value, True)
            unicommetadata.set("{%s}value" % Common.XML_NAMESPACE, value)

def merge_xml_change_pkg(gamefolder, payfolder, newpkgname):
    Log.out("[Logging...] 正在合并文件 : [AndroidManifest.xml]", True)
    if (os.path.exists(gamefolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    gamemanifest = "%s/AndroidManifest.xml" % gamefolder;
    paymanifest = "%s/AndroidManifest.xml" % payfolder;
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

    pkgname = gameroot.get("package")
    if (newpkgname != None and newpkgname != ""):
        #修改包名
        Log.out("[Logging...] 使用配置包名 : [%s]" % newpkgname, True)
        gameroot.set("package", newpkgname)
        pkgname = newpkgname
    #修改联通
    modify_unicom_metadata(gameroot)
    #去除重复的权限
    remove_dup_permission(gameroot)
    #去除敏感权限
    remove_sensitive_permission(gameroot)
    #添加入口activity
    #add_entry_activity(gameroot)
    #关键组建检测
    key_component_check(gameroot)
    indent(gameroot)
    gametree.write(gamemanifest, encoding='utf-8', xml_declaration=True)

    f = open(gamemanifest, "r")
    rc = f.read()

    #修改pay action
    rc = modify_pay_action(rc, pkgname)
    #修改包名
    #rc = modify_pkgname(rc, pkgname, newpkgname)

    f.close()
    f = open(gamemanifest, "w")
    f.write(rc)
    f.close()
    Log.out("[Logging...] 文件合并完成\n", True)
    return True

if __name__ == "__main__":
    merge_xml(sys.argv[1], sys.argv[2])