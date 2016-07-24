#!/usr/bin/python
# coding: UTF-8

import os
import sys
import shutil
import platform

def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        print("操作完成，按任意键退出")
        msvcrt.getch()

def copydir(fromdir, todir):
    mylist = os.walk(fromdir, True)
    for root, filedir, files in mylist:
        for file in files:
            todirname = root.replace(fromdir, todir)
            if (os.path.exists(todirname) == False):
                os.makedirs(todirname)
            #sdk文件夹内的文件
            fromdirfile = os.path.join(root, file)
            todirfile = fromdirfile.replace(fromdir, todir)
            copyfile(fromdirfile, todirfile)

def copyfile(fromfile, tofile):
    try:
        shutil.copy2(fromfile, tofile)
    except:
        pass

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

#安全获取字典的值
def getvalue(item, key):
    try:
        return item[key]
    except:
        return None

#获取xml的节点属性
def getattrib(item, key):
    try:
        return item.attrib[key];
    except:
        return None

#规范化路径名称
def normalPath(path):
    return os.path.normpath(path)

def exitOnFalse(ret):
    if (ret == False):
        sys.exit()

def isEmpty(string):
    if (string == None or string.strip() == ""):
        return True
    return False