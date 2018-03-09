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

def merge_xml(masterfolder, slavefolder):
    merge_xml_change_pkg(masterfolder, slavefolder, None)

#查找原插件app中的启动Activity
def findEntryActivity(root):
    entryNode = root.find(Common.MAIN_ACTIVITY_XPATH)
    if (entryNode != None):
        return entryNode

def processEntryActivity(decompiledfolder, masterroot, slaveroot):
    appEntryNode = findEntryActivity(masterroot)
    sdkEntryNode = findEntryActivity(slaveroot)

    master_entry = None
    slave_entry = None

    if appEntryNode != None:
        master_entry = appEntryNode.attrib['{%s}name' % Common.XML_NAMESPACE]
    if sdkEntryNode != None:
        slave_entry = sdkEntryNode.attrib['{%s}name' % Common.XML_NAMESPACE]

    if master_entry != None and master_entry != '' and slave_entry != None and slave_entry != '':
        intentFilterNode = appEntryNode.find("intent-filter/category/[@{%s}name='android.intent.category.LAUNCHER']/.." % Common.XML_NAMESPACE)
        categoryNode = intentFilterNode.find('category')
        if intentFilterNode != None and categoryNode != None:
            intentFilterNode.remove(categoryNode)
            package = masterroot.get("package")
            if master_entry.startswith("."):
                master_entry = package + master_entry
    return master_entry, slave_entry

#添加入口activity到主activity
def check_ad_entry_activity(item, master_entry, slave_entry):
    if slave_entry == None:
        return
    activityName = item.attrib["{%s}name" % Common.XML_NAMESPACE]
    if (activityName == slave_entry):
        element = ET.Element("meta-data")
        element.set("{%s}name" % Common.XML_NAMESPACE, "app_entry_name")
        element.set("{%s}value" % Common.XML_NAMESPACE, master_entry)
        item.append(element)

#去除重复权限
def remove_dup_permission(masterroot):
    Log.out("[Logging...] 去除重复权限", True)
    permissions = masterroot.findall(".//uses-permission")
    perlist = []
    if (permissions != None):
        for item in permissions:
            permisson_name = item.attrib["{%s}name" % Common.XML_NAMESPACE]
            if (permisson_name in perlist):
                masterroot.remove(item)
            else:
                perlist += [permisson_name]

def merge_xml_change_pkg(masterfolder, slavefolder, newpkgname = None):
    Log.out("[Logging...] 正在合并文件 : [AndroidManifest.xml]", True)
    if (os.path.exists(masterfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % masterfolder, True)
        sys.exit(0)
    if (os.path.exists(slavefolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % slavefolder, True)
        sys.exit(0)
    mastermanifest = "%s/AndroidManifest.xml" % masterfolder;
    slavemanifest = "%s/AndroidManifest.xml" % slavefolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    mastertree = ET.parse(mastermanifest)
    masterroot = mastertree.getroot()
    masterapplication = masterroot.find("application")

    slavetree = ET.parse(slavemanifest)
    slaveroot = slavetree.getroot()
    slaveapplication = slaveroot.find("application")

    #处理入口Activity
    #master_entry, slave_entry = processEntryActivity(masterfolder, masterroot, slaveroot)

    for item in slaveroot.getchildren():
        if (item.tag == "uses-permission"):
            masterroot.append(item)

    for item in slaveapplication.getchildren():
        exclude = item.find("meta-data/[@{%s}name='exclude']" % Common.XML_NAMESPACE)
        if (exclude == None):
            #check_ad_entry_activity(item, master_entry, slave_entry)
            masterapplication.append(item)

    #去除重复的权限
    remove_dup_permission(masterroot)

    indent(masterroot)
    mastertree.write(mastermanifest, encoding='utf-8', xml_declaration=True)

    Log.out("[Logging...] 文件合并完成\n", True)
    return True

if __name__ == "__main__":
    merge_xml_change_pkg(sys.argv[1], sys.argv[2])