#!/usr/bin/python
# coding: UTF-8
# encoding:utf-8
import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import Common
import Log

import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document

def add_gb_string(publicroot, gamefolder):

    gamemanifest = "%s/AndroidManifest.xml" % gamefolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)
    gametree = ET.parse(gamemanifest)
    gameroot = gametree.getroot()
    activity_entry_value = None
    paymetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (Common.XML_NAMESPACE, Common.PAY_ACTIVITY, Common.XML_NAMESPACE, Common.PAYACTIVITY_ENTRY_NAME))
    if (paymetadata != None):
        activity_entry_value = paymetadata.get("{%s}value" % Common.XML_NAMESPACE)
    if (activity_entry_value == None):
        return []

    if (check_name_exists(publicroot, "g_class_name", "string") == False):    
        gbstringfile = "%s/res/values/njck1_strings.xml" % gamefolder
        doc = Document()  #创建DOM文档对象
        gbstring = doc.createElement("string")
        gbstring.setAttribute("name", "g_class_name")
        textnode = doc.createTextNode(activity_entry_value)
        gbstring.appendChild(textnode)
        Log.out("[Logging...] 添加基地入口 : [%s]\n" % activity_entry_value, True)
        return [gbstring]
    else:
        Log.out("[Logging...] 基地入口存在\n", True)
        return []

def check_name_exists(root, name, type):
    list = root.findall(".//public[@name='%s'][@type='%s']" % (name, type))
    if (len(list) <= 0):
        return False
    return True

def add_extra_string(publicroot, gamefolder, company_name):
    list = []
    list += add_gb_string(publicroot, gamefolder)

    if (len(list) <= 0):
        return
    gbstringfile = "%s/res/values/njck_extra_strings.xml" % gamefolder
    doc = Document()  #创建DOM文档对象
    root = doc.createElement('resources') #创建根元素
    doc.appendChild(root)
    for item in list:
        root.appendChild(item)
    f = open(gbstringfile,'wb')
    f.write(doc.toxml(encoding = "utf-8"))
    f.close()
    tree = ET.parse(gbstringfile)
    indent(tree.getroot())
    tree.write(gbstringfile, encoding="utf-8", xml_declaration=True)

def merge_extra(gamefolder, company_name):
    if (os.path.exists(gamefolder) == False):
        Log.out("[Warning...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    Log.out("[Logging...] 添加额外资源", True)
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    tree = ET.parse(gamepublic)
    root = tree.getroot()
    add_extra_string(root, gamefolder, company_name)

if __name__ == "__main__":
    rebuild_ids(sys.argv[1], sys.argv[2])