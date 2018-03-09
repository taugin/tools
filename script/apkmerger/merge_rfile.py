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
import re
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
    '''    此方法用来检测重复的资源    '''
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

###############################################################################
def find_rfolder(smali_folder):
    rtmp = []
    file_list = os.walk(smali_folder, True)
    for root, filedir, files in file_list:
        tmplist = os.listdir(root)
        if (tmplist != None and len(tmplist) > 0):
            filetmps = []
            for index in range(len(tmplist)):
                ret = re.search("^R.smali", tmplist[index])
                if (ret == None):
                    ret = re.search("^R\$(.*).smali", tmplist[index])
                if (ret != None):
                    filetmps += [tmplist[index]]
            if (len(filetmps) > 1 and "R.smali" in filetmps):
                rtmp += [root]
    return rtmp

def find_all_rfolders(masterfolder):
    rfolders = []
    smali_folder = os.path.join(masterfolder, "smali")
    folder = find_rfolder(smali_folder)
    if (folder != None):
        rfolders += folder
    smali_folder = os.path.join(masterfolder, "smali_classes2")
    folder = find_rfolder(smali_folder)
    if (folder != None):
        rfolders += folder
    smali_folder = os.path.join(masterfolder, "smali_classes3")
    folder = find_rfolder(smali_folder)
    if (folder != None):
        rfolders += folder
    return rfolders
#---------------------------------------------------------------------#

def find_rfiles(rfolder):
    rfiles = []
    mylist = os.walk(rfolder, True)
    for root, filedir, files in mylist:
        for file in files:
            if (file.startswith("R$")):
                rfiles += [os.path.join(root, file)]
    return rfiles

def update_one_rfile(pubdict, rfile):
    #Log.out("update rfile : %s" % rfile)
    conlist = []
    f = open(rfile, "r");
    allcontent = f.readlines()
    for c in allcontent:
        conlist.append(c.replace("\n", ""))
    f.close()
    name = None
    oid = None
    nid = None
    modify = False
    for index in range(len(conlist)):
        c = conlist[index]
        if (c.startswith(".field public static")):
            s = c.split(r" ")
            try:
                name = s[4].split(":")[0]
                oid = s[6]
                nid = pubdict[name]
                if (nid != oid):
                    s[6] = nid
                    news = " ".join(s)
                    #Log.out("%s -> %s" % (c, news))
                    conlist[index] = news
                    modify = True
            except:
                pass
    if (modify) :
        newcontent = "\n".join(conlist)
        f = open(rfile, "w")
        f.write(newcontent)
        f.close()

def update_one_rfolder(pubdict, rfolder):
    r_files = find_rfiles(rfolder)
    for f in r_files:
        update_one_rfile(pubdict, f)

def update_all_rfile(masterfolder):
    ''' 重建R文件 '''
    Log.out("[Logging...] 重建资源文件", True)
    all_rfolder = find_all_rfolders(masterfolder)
    #Log.out("all_rfolder : %s" % all_rfolder)
    if (all_rfolder != None and len(all_rfolder) > 0):
        pubdict = prepare_public(masterfolder)
    for folder in all_rfolder:
        update_one_rfolder(pubdict, folder)

def prepare_public(masterfolder):
    pubdict = {}
    publicxml = os.path.join(masterfolder, "res", "values", "public.xml");
    if (os.path.exists(publicxml)):
        tree = ET.parse(publicxml)
        if (tree == None):
            return None
        root = tree.getroot()
        if (root == None):
            return None
        items = root.getchildren()
        for item in items:
            pubdict[item.get("name")] = item.get("id")
    return pubdict

if __name__ == "__main__":
    update_all_rfile("D:\\temp\\loseweight-merged-final")