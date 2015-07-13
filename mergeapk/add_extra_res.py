#!/usr/bin/python
# coding: UTF-8
# encoding:utf-8
import os
import sys
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document

XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

COCOSPAY_ACTIVITY = "com.cocospay.CocosPayActivity"
COCOSPAYACTIVITY_ENTRY_NAME = "dest_activity"

MAX_STRING_ID = ""

def log(str, show=False):
    if (show):
        print(str)

def add_gb_string(root, dict, maxids, gamefolder):
    if (check_name_exists(root, "g_class_name", "string") == True):
        return []

    gamemanifest = "%s/AndroidManifest.xml" % gamefolder;
    ET.register_namespace('android', XML_NAMESPACE)
    gametree = ET.parse(gamemanifest)
    gameroot = gametree.getroot()
    activity_entry_value = None
    cocospaymetadata = gameroot.find(".//activity/[@{%s}name='%s']/meta-data[@{%s}name='%s']" % (XML_NAMESPACE, COCOSPAY_ACTIVITY, XML_NAMESPACE, COCOSPAYACTIVITY_ENTRY_NAME))
    if (cocospaymetadata != None):
        activity_entry_value = cocospaymetadata.get("{%s}value" % XML_NAMESPACE)
    if (activity_entry_value == None):
        return []

    type = "string"
    hexid = get_next_id(type, dict, maxids)
    element = ET.Element("public")
    element.attrib["id"] = hexid
    element.attrib["name"] = "g_class_name"
    element.attrib["type"] = "string"
    root.append(element)
    
    gbstringfile = "%s/res/values/njck1_strings.xml" % gamefolder
    doc = Document()  #创建DOM文档对象
    gbstring = doc.createElement("string")
    gbstring.setAttribute("name", "g_class_name")
    textnode = doc.createTextNode(activity_entry_value)
    gbstring.appendChild(textnode)
    log("[Logging...] 添加基地入口 : [%s]" % activity_entry_value, True)
    return [gbstring]

def check_name_exists(root, name, type):
    list = root.findall(".//public[@name='%s'][@type='%s']" % (name, type))
    if (len(list) <= 0):
        return False
    return True

def add_company_string(root, dict, maxids, gamefolder, company_name):
    if (check_name_exists(root, "PARTNER_NAME", "string") == True):
        return []

    log("[Logging...] 配置公司名称 : [%s]" % company_name, True)
    if (company_name == None or company_name == ""):
        return []

    type = "string"
    hexid = get_next_id(type, dict, maxids)
    element = ET.Element("public")
    element.attrib["id"] = hexid
    element.attrib["name"] = "PARTNER_NAME"
    element.attrib["type"] = "string"
    root.append(element)

    doc = Document()  #创建DOM文档对象
    gbstring = doc.createElement("string")
    gbstring.setAttribute("name", "PARTNER_NAME")
    textnode = doc.createTextNode(company_name)
    gbstring.appendChild(textnode)

    return [gbstring]

def add_extra_string(root, dict, maxids, gamefolder, company_name):
    list = []
    list += add_gb_string(root, dict, maxids, gamefolder)
    #list += add_company_string(root, dict, maxids, gamefolder, company_name)

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

def get_max_stringid(gamefolder):
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    if (os.path.exists(gamepublic) == False):
        log("[Error...] 无法定位文件 %s" % gamepublic, True)
        sys.exit(0)
    tree = ET.parse(gamepublic)
    root = tree.getroot()
    stringlist = root.findall(".//public/[@type='string']");
    log(stringlist, True)
    for s in stringlist:
        log(s, True)

def add_extra_res(gamefolder):
    if (os.path.exists(gamefolder) == False):
        log("[Error...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    log("[Logging...] 添加额外资源", True)
    get_max_stringid(gamefolder)

if (__name__ == "__main__"):
    add_extra_res(sys.argv[1])