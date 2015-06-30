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

def check_public(gamefolder, payfolder):
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    paypublic = "%s/res/values/public.xml" % payfolder;

    gameidlist = readislist(gamepublic)
    payidlist = readislist(paypublic)

    logfile = open("dup.txt", "w");
    idexist = False
    for text in gameidlist:
        exist = exist_in(text, payidlist)
        if (exist == True):
            idexist = True
            logfile.write(text + "\n")
            log("%s exist : %s" % (text, exist_in(text, payidlist)))
    logfile.close()
    return idexist;

def check_lib_assets(gamefolder, payfolder):
    exist = False
    logfile = open("dup.txt", "a");
    checkpath = os.path.join(gamefolder, "lib")
    list = os.walk(checkpath, True)
    for root, dirs, files in list:
        for file in files:
            filedir = os.path.join(root, file)
            payfile = filedir.replace(gamefolder, payfolder)
            if (os.path.exists(payfile) == True):
                logfile.write(filedir + "\n")
                exist = True

    checkpath = os.path.join(gamefolder, "assets")
    list = os.walk(checkpath, True)
    for root, dirs, files in list:
        for file in files:
            filedir = os.path.join(root, file)
            payfile = filedir.replace(gamefolder, payfolder)
            if (os.path.exists(payfile) == True):
                logfile.write(filedir + "\n")
                exist = True
    logfile.close()
    return exist;

def check_dup(gamefolder, payfolder):
    if (os.path.exists(gamefolder) == False or os.path.exists(payfolder) == False):
        log("[Error...] 无法定位文件夹 %s or %s" % (gamefolder, payfolder))
    filedup = False
    id_dup = check_public(gamefolder, payfolder)
    filedup = check_lib_assets(gamefolder, payfolder)
    all_dup = id_dup or filedup
    log("Has Dup Files : %s " % all_dup, True)

check_dup(sys.argv[1], sys.argv[2])