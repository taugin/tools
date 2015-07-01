#!/usr/bin/python
# coding: UTF-8

import os
import sys
import xml.etree.ElementTree as ET

def log(str, show=False):
    if (show):
        print(str)

def readislist(publicfile):
    tree = ET.parse(publicfile)
    root = tree.getroot();
    list = []
    for child in root:
        list.append("%s#%s" % (child.attrib["type"], child.attrib["name"]))
    return list

def exist_in(text, list):
    return text in list

def check_public(gamefolder, payfolder, dup_list):
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    paypublic = "%s/res/values/public.xml" % payfolder;

    gameidlist = readislist(gamepublic)
    payidlist = readislist(paypublic)

    idexist = False
    for text in gameidlist:
        exist = exist_in(text, payidlist)
        if (exist == True):
            idexist = True
            dup_list.append(text + "\n")
            log("%s exist : %s" % (text, exist_in(text, payidlist)))
    return idexist;

def check_lib_assets(gamefolder, payfolder, dup_list):
    exist = False
    checkpath = os.path.join(gamefolder, "lib")
    list = os.walk(checkpath, True)
    for root, dirs, files in list:
        for file in files:
            filedir = os.path.join(root, file)
            payfile = filedir.replace(gamefolder, payfolder)
            if (os.path.exists(payfile) == True):
                dup_list.append(filedir + "\n")
                exist = True

    checkpath = os.path.join(gamefolder, "assets")
    list = os.walk(checkpath, True)
    for root, dirs, files in list:
        for file in files:
            filedir = os.path.join(root, file)
            payfile = filedir.replace(gamefolder, payfolder)
            if (os.path.exists(payfile) == True and (file != "ItemMapper.xml" and file != "plugins.xml")):
                dup_list.append(filedir + "\n")
                exist = True
    return exist;

def check_dup(gamefolder, payfolder):
    dup_list = []
    if (os.path.exists(gamefolder) == False):
        log("[Error...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        log("[Error...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    log("[Logging...] 正在检查重复资源", True)
    filedup = False
    id_dup = check_public(gamefolder, payfolder, dup_list)
    filedup = check_lib_assets(gamefolder, payfolder, dup_list)
    all_dup = id_dup or filedup
    if (all_dup == True):
        log("[Logging...] 有重复资源 \n", True)
        f = open("dup.txt", "w")
        for s in dup_list:
            f.write(s)
        f.close()
        return False
    else:
        if (os.path.exists("dup.txt")):
            os.remove("dup.txt")
        log("[Logging...] 无重复资源 \n", True)
        return True

if __name__ == "__main__":
    check_dup(sys.argv[1], sys.argv[2])