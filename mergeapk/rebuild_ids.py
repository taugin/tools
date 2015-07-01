#!/usr/bin/python
# coding: UTF-8

import os
import sys
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

def log(str, show=False):
    if (show):
        print(str)

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
    indent(gameroot)
    gametree.write(gamepublic)
    log("[Logging...] 重建资源ID完成\n", True)
    return True

if __name__ == "__main__":
    rebuild_ids(sys.argv[1], sys.argv[2])