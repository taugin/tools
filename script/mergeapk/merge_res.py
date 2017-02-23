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

import shutil
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

def merge_res(gamefolder, payfolder):
    Log.out("[Logging...] 拷贝资源文件 : [res]", True)
    if (os.path.exists(gamefolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    gameres = os.path.join(gamefolder, "res")
    payres = os.path.join(payfolder, "res")
    list = os.walk(payres, True)
    for root, dirs, files in list:
        for file in files:
            gamedir = root.replace(payfolder, gamefolder)
            payfile = os.path.join(root, file)
            if (os.path.exists(gamedir) == False):
                os.makedirs(gamedir)
            if (root.endswith("values") == False):
                gamefile = payfile.replace(payfolder, gamefolder)
                #Log.out("payfile : %s , gamefile : %s " % (payfile, gamefile))
                shutil.copy2(payfile, gamefile)
            else:
                if (file != "public.xml"):
                    file = "njck_" + file
                    tmp = os.path.join(root, file)
                    gamefile = tmp.replace(payfolder, gamefolder)
                    #Log.out("payfile : %s , gamefile : %s " % (payfile, gamefile))
                    shutil.copy2(payfile, gamefile)
    njck_stringfile = "%s/res/values/njck_strings.xml" % gamefolder
    if (os.path.exists(njck_stringfile)):
        tree = ET.parse(njck_stringfile)
        root = tree.getroot()
        element = root.find(".//string[@name='g_class_name']")
        if (element != None):
            Log.out("[Logging...] 删除基地入口 : [%s]" % element.text, True)
            root.remove(element)
            indent(root)
            tree.write(njck_stringfile, encoding="utf-8", xml_declaration=True)
    Log.out("[Logging...] 拷贝资源完成\n", True)
    return True

if __name__ == "__main__":
    copy_res(sys.argv[1], sys.argv[2])