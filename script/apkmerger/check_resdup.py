#!/usr/bin/python
# coding: UTF-8

'''
检测是否有重复资源，检测的目录包括assets,res,lib
'''
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

def readislist(publicfile):
    tree = ET.parse(publicfile)
    root = tree.getroot();
    list = []
    for child in root:
        list.append("%s#%s" % (child.attrib["type"], child.attrib["name"]))
    return list

def exist_in(text, list):
    return text in list

#检测res中是否有重复的资源，包括layout,drawable,strings,color 等等
#通过检测public.xml可以完成
def check_public(gamefolder, payfolder, dup_list):
    gamepublic = "%s/res/values/public.xml" % gamefolder;
    paypublic = "%s/res/values/public.xml" % payfolder;
    if (os.path.exists(gamepublic) == False):
        Log.out("[Warning...] 无法定位文件 %s" % gamepublic, True)
        return False
    if (os.path.exists(paypublic) == False):
        Log.out("[Warning...] 无法定位文件 %s" % paypublic, True)
        return False
    gameidlist = readislist(gamepublic)
    payidlist = readislist(paypublic)

    idexist = False
    for text in gameidlist:
        exist = exist_in(text, payidlist)
        if (exist == True):
            idexist = True
            dup_list.append(text + "\n")
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

def check_resdup(gamefolder, payfolder):
    dup_list = []
    if (os.path.exists(gamefolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    Log.out("[Logging...] 检查重复资源", True)
    filedup = False
    id_dup = check_public(gamefolder, payfolder, dup_list)
    #filedup = check_lib_assets(gamefolder, payfolder, dup_list)
    all_dup = id_dup or filedup
    if (all_dup == True):
        Log.out("[Logging...] 存在重复资源, 请检查\n", True)
        '''
        f = open("dup.txt", "w")
        for s in dup_list:
            f.write(s)
        f.close()
        '''
        return True
    else:
        if (os.path.exists("dup.txt")):
            os.remove("dup.txt")
        Log.out("[Logging...] 没有重复资源 \n", True)
        return True

if __name__ == "__main__":
    check_resdup(sys.argv[1], sys.argv[2])