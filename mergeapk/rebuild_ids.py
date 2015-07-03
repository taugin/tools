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
ACTIVITY_ENTRY_NAME = "dest_activity"

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
    for item in gameroot.iter('meta-data'):
        if (item.get("{%s}name" % XML_NAMESPACE) == ACTIVITY_ENTRY_NAME):
            activity_entry_value = item.get("{%s}value" % XML_NAMESPACE)
    if (activity_entry_value == None):
        return []

    maxid = maxids["string"]
    maxid = process_maxid(maxid, dict, type)
    intid = int(eval(maxid))
    intid = intid + 1
    hexid = hex(intid)
    maxids[type] = hexid
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

    return [gbstring]

def check_name_exists(root, name, type):
    list = root.findall(".//public[@name='%s'][@type='%s']" % (name, type))
    if (len(list) <= 0):
        return False
    return True

def add_company_string(root, dict, maxids, gamefolder):
    if (check_name_exists(root, "PARTNER_NAME", "string") == True):
        return []
    maxid = maxids["string"]
    maxid = process_maxid(maxid, dict, type)
    intid = int(eval(maxid))
    intid = intid + 1
    hexid = hex(intid)
    maxids[type] = hexid
    element = ET.Element("public")
    element.attrib["id"] = hexid
    element.attrib["name"] = "PARTNER_NAME"
    element.attrib["type"] = "string"
    root.append(element)

    company_name = "上海触控有限公司"
    doc = Document()  #创建DOM文档对象
    gbstring = doc.createElement("string")
    gbstring.setAttribute("name", "PARTNER_NAME")
    textnode = doc.createTextNode(company_name)
    gbstring.appendChild(textnode)

    return [gbstring]

def add_extra_string(root, dict, maxids, gamefolder):
    list = []
    list += add_gb_string(root, dict, maxids, gamefolder)
    list += add_company_string(root, dict, maxids, gamefolder)

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

def gettypeid(publicfile):
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

def getmaxids(dict, key):
    if (key not in dict):
        return "0x0"
    list = dict[key]
    list.sort()
    return list[-1]

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

def process_maxid(maxid, dict, type):
    if (maxid != "0x0"):
        return maxid

    #log("maxid : %s" % maxid)
    idlist = []
    for key in dict:
        list = dict[key]
        list.sort()
        #log("type : %s, key : %s, item : %s" % (type, key,list[0]))
        idlist.append(list[0][0:6])
    idlist.sort()
    intid = int(eval(idlist[-1]))
    intid = intid + 1
    hexid = hex(intid) + "0000"
    dict[type] = [hexid]
    log("unfind id : %s" % hexid)
    return hexid

def rebuild_ids(gamefolder, payfolder):
    if (os.path.exists(gamefolder) == False):
        log("[Error...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        log("[Error...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    log("[Logging...] 正在重建资源ID", True)
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    paypublic = "%s/res/values/public.xml" % payfolder;
    dict = gettypeid(gamepublic)

    tree = ET.parse(paypublic)
    root = tree.getroot();
    list = []
    maxids = {}

    gametree = ET.parse(gamepublic)
    gameroot = gametree.getroot()

    for child in root:
        type = child.attrib["type"]
        name = child.attrib["name"]
        id = child.attrib["id"]

        if (type not in maxids):
            maxid = getmaxids(dict, type)
            maxids[type] = maxid
        #log(maxids[type])
        maxid = process_maxid(maxids[type], dict, type)
        #log(maxid)
        intid = int(eval(maxid))
        intid = intid + 1
        hexid = hex(intid)
        maxids[type] = hexid
        #element = ET.XML('<public type="%s" name="%s" id="%s" />' % (type, name, hexid))
        element = ET.Element("public")
        element.attrib["id"] = hexid
        element.attrib["name"] = name
        element.attrib["type"] = type
        gameroot.append(element)
    add_extra_string(gameroot, dict, maxids, gamefolder)
    indent(gameroot)
    gametree.write(gamepublic, encoding="utf-8", xml_declaration=True)
    log("[Logging...] 重建资源ID完成\n", True)
    return True

if __name__ == "__main__":
    rebuild_ids(sys.argv[1], sys.argv[2])