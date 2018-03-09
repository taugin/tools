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

def merge_exist(masterfile, slavefile, override):
    #Log.out("[Logging...] 合并 %s -> %s" % (slavefile, masterfile))
    try:
        mastertree = ET.parse(masterfile)
        slavetree = ET.parse(slavefile)
        masterroot = mastertree.getroot();
        slaveroot = slavetree.getroot()

        masterchildren = masterroot.getchildren()
        slavechildren = slaveroot.getchildren()
        if (len(slavechildren) <= 0):
            #如果资源内容为空，则不需要合并
            return True
        namelist = {}
        for item in masterchildren:
            namelist[item.get("name")] = item

        for item in slavechildren:
            if (item != None):
                name = item.get("name")
                value = None
                if (name != None and name in namelist.keys()):
                    value = namelist[name]
                #资源不存在时
                if value == None:
                    masterroot.append(item)
                else:
                    #资源存在时
                    if (override == True):
                        masterroot.remove(value)
                        masterroot.append(item)
        indent(masterroot)
        mastertree.write(masterfile, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        Log.out("Exception : %s" % e)

def merge_res(masterfolder, slavefolder, override = False):
    Log.out("[Logging...] 拷贝资源文件 : [res]", True)
    if (os.path.exists(masterfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % masterfolder, True)
        sys.exit(0)
    if (os.path.exists(slavefolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % slavefolder, True)
        sys.exit(0)
    masterres = os.path.join(masterfolder, "res")
    slaveres = os.path.join(slavefolder, "res")
    list = os.walk(slaveres, True)
    for root, dirs, files in list:
        for file in files:
            masterdir = root.replace(slavefolder, masterfolder)
            slavefile = os.path.join(root, file)
            if (os.path.exists(masterdir) == False):
                os.makedirs(masterdir)
            #拷贝其他文件夹里面的内容
            if (os.path.basename(root).startswith("values") == False):
                masterfile = slavefile.replace(slavefolder, masterfolder)
                #Log.out("slavefile : %s , masterfile : %s " % (slavefile, masterfile))
                shutil.copy2(slavefile, masterfile)
            #拷贝values文件夹里面的内容
            else:
                if (file == "public.xml"):
                    #不处理public.xml文件
                    continue
                tmp = os.path.join(root, file)
                masterfile = tmp.replace(slavefolder, masterfolder)
                if (os.path.exists(masterfile)) :
                    merge_exist(masterfile, slavefile, override)
                else:
                    #Log.out("slavefile : %s , masterfile : %s " % (slavefile, masterfile))
                    shutil.copy2(slavefile, masterfile)
    Log.out("[Logging...] 拷贝资源完成\n", True)
    return True

if __name__ == "__main__":
    merge_res(sys.argv[1], sys.argv[2])