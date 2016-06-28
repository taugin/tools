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

def add_gb_string(root, dict, maxids, gamefolder):

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

    if (check_name_exists(root, "g_class_name", "string") == False):
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
    Log.out("[Logging...] 添加基地入口 : [%s]" % activity_entry_value, True)
    return [gbstring]

def check_name_exists(root, name, type):
    list = root.findall(".//public[@name='%s'][@type='%s']" % (name, type))
    if (len(list) <= 0):
        return False
    return True

def add_extra_string(root, dict, maxids, gamefolder, company_name):
    list = []
    list += add_gb_string(root, dict, maxids, gamefolder)

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

#获取所有的ID
def get_all_ids(publicfile):
    tree = ET.parse(publicfile)
    root = tree.getroot()
    dict = {}
    for child in root:
        type = child.attrib["type"]
        name = child.attrib["name"]
        id = child.attrib["id"]
        if (type in dict):
            dict[type].append(id)
        else:
            dict[type] = [id]

    return dict;

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

#查找public中类型的最大ID，如果ID不存在，则
#在所有类型的最大值中+1
#如：layout不存在public中，则找出所有类型的最大ID
#即0x7f03，然后将此值+1为0x7f04，最后将此值与0000
#合并成ID ：0x7f040000
def process_maxid(maxid, dict, type):
    if (maxid != "unknown"):
        return maxid

    idlist = []
    for key in dict:
        list = dict[key]
        list.sort()
        idlist.append(list[0][0:6])
    idlist.sort()
    intid = 0
    if (len(idlist) > 0):
        intid = int(eval(idlist[-1]))
    else:
        intid = int(eval("0x7f01"))
    intid = intid + 1
    hexid = hex(intid) + "0000"
    dict[type] = [hexid]
    return hexid

#获取特定类型的最大ID，如果不存在返回unknown
def getmaxids(dict, key):
    if (key not in dict):
        return "unknown"
    list = dict[key]
    list.sort()
    return list[-1]

#获取当前最大的ID值，然后+1，作为下一个
#ID值
def get_next_id(type, dict, maxids):
    if (type not in maxids):
        maxid = getmaxids(dict, type)
        maxids[type] = maxid
    maxid = process_maxid(maxids[type], dict, type)
    intid = int(eval(maxid))
    intid = intid + 1
    hexid = hex(intid)
    maxids[type] = hexid
    return hexid

#生成空的public.xml文件
def generate_xml(public_xml):
    dir = os.path.dirname(public_xml)
    os.makedirs(dir)
    doc = Document()  #创建DOM文档对象
    root = doc.createElement('resources') #创建根元素
    doc.appendChild(root)
    #element = doc.createElement("public")
    #element.setAttribute("id", "0x7f000000")
    #element.setAttribute("name", "empty")
    #element.setAttribute("type", "undefine")
    #root.appendChild(element)

    f = open(public_xml,'wb')
    f.write(doc.toxml(encoding = "utf-8"))
    f.close()
    tree = ET.parse(public_xml)
    indent(tree.getroot())
    tree.write(public_xml, encoding="utf-8", xml_declaration=True)

def rebuild_ids(gamefolder, payfolder, company_name):
    if (os.path.exists(gamefolder) == False):
        Log.out("[Warning...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        Log.out("[Warning...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    Log.out("[Logging...] 重建资源编号", True)
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    paypublic = "%s/res/values/public.xml" % payfolder;
    if (os.path.exists(gamepublic) == False):
        Log.out("[Warning...] 无法定位文件 %s\n" % gamepublic, True)
        generate_xml(gamepublic)

    if (os.path.exists(paypublic) == False):
        Log.out("[Warning...] 无法定位文件 %s\n" % paypublic, True)
        generate_xml(paypublic)

    dict = get_all_ids(gamepublic)

    tree = ET.parse(paypublic)
    root = tree.getroot();
    list = []
    maxids = {}
    for type in dict:
        maxid = getmaxids(dict, type)
        maxids[type] = maxid

    gametree = ET.parse(gamepublic)
    gameroot = gametree.getroot()

    for child in root:
        type = child.attrib["type"]
        name = child.attrib["name"]
        id = child.attrib["id"]

        hexid = get_next_id(type, dict, maxids)

        element = ET.Element("public")
        element.attrib["id"] = hexid
        element.attrib["name"] = name
        element.attrib["type"] = type
        gameroot.append(element)
    add_extra_string(gameroot, dict, maxids, gamefolder, company_name)
    indent(gameroot)
    gametree.write(gamepublic, encoding="utf-8", xml_declaration=True)
    Log.out("[Logging...] 重建资源完成\n", True)
    return True

if __name__ == "__main__":
    rebuild_ids(sys.argv[1], sys.argv[2])