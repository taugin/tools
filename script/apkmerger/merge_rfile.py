#!/usr/bin/python
# coding: UTF-8

'''
基本思想：
1. 查找smali中所有的R文件，包含R文件的子类文件（通过^R.smali 或者^R\$(.*).smali）
2. 在public.xml中提取出所有的资源ID
3. 按照public.xml中的资源ID，更新smali文件中的ID
4. 严格使用类型+名称作为唯一识别
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

def read_idlist(publicfile):
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
def check_public(masterfolder, slavefolder, dup_list):
    masterpublic = "%s/res/values/public.xml" % masterfolder;
    slavepublic = "%s/res/values/public.xml" % slavefolder;
    if (os.path.exists(masterpublic) == False):
        Log.out("[Warning...] 无法定位文件 %s" % masterpublic, True)
        return False
    if (os.path.exists(slavepublic) == False):
        Log.out("[Warning...] 无法定位文件 %s" % slavepublic, True)
        return False
    masteridlist = read_idlist(masterpublic)
    slaveidlist = read_idlist(slavepublic)

    idexist = False
    for text in masteridlist:
        exist = exist_in(text, slaveidlist)
        if (exist == True):
            idexist = True
            dup_list.append(text + "\n")
    return idexist;

def check_lib_assets(masterfolder, slavefolder, dup_list):
    exist = False
    checkpath = os.path.join(masterfolder, "lib")
    rlist = os.walk(checkpath, True)
    for root, dirs, files in rlist:
        for file in files:
            filedir = os.path.join(root, file)
            slavefile = filedir.replace(masterfolder, slavefolder)
            if (os.path.exists(slavefile) == True):
                dup_list.append(filedir + "\n")
                exist = True

    checkpath = os.path.join(masterfolder, "assets")
    rlist = os.walk(checkpath, True)
    for root, dirs, files in rlist:
        for file in files:
            filedir = os.path.join(root, file)
            slavefile = filedir.replace(masterfolder, slavefolder)
            if (os.path.exists(slavefile) == True):
                dup_list.append(filedir + "\n")
                exist = True
    return exist;

def check_resdup(masterfolder, slavefolder):
    '''    此方法用来检测重复的资源    '''
    dup_list = []
    if (os.path.exists(masterfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % masterfolder, True)
        sys.exit(0)
    if (os.path.exists(slavefolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % slavefolder, True)
        sys.exit(0)
    Log.out("[Logging...] 检查重复资源", True)
    filedup = False
    id_dup = check_public(masterfolder, slavefolder, dup_list)
    #filedup = check_lib_assets(masterfolder, slavefolder, dup_list)
    all_dup = id_dup or filedup
    if (all_dup == True):
        Log.out("[Logging...] 存在重复资源 : 请检查\n", True)
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
            if (len(filetmps) > 1):
                if "R.smali" in filetmps:
                    rtmp += [root]
                else:
                    Log.out("[Logging...] 缺失关键文件 : [%s]" % os.path.join(root, "R.smali"))
    return rtmp

def find_all_rfolders(masterfolder):
    rfolders = []
    all_smali_folder = ["smali", "smali_classes2", "smali_classes3", "smali_classes4", "smali_classes5", "smali_classes6", "smali_classes7", "smali_classes8", "smali_classes9", "smali_classes10"]
    for tmp_folder in all_smali_folder:
        smali_folder = os.path.join(masterfolder, tmp_folder)
        if (os.path.exists(smali_folder)):
            folder = find_rfolder(smali_folder)
            if (folder != None):
                rfolders += folder
        else:
            break;
    return rfolders
#---------------------------------------------------------------------#

def find_rfiles(rfolder):
    '''查找一个文件夹下面所有的R$开头的文件'''
    rfiles = []
    mylist = os.walk(rfolder, True)
    for root, filedir, files in mylist:
        for file in files:
            if (file.startswith("R$")):
                rfiles += [os.path.join(root, file)]
    return rfiles

def find_type_byfile(rfile):
    '''通过文件名字查找类型名字'''
    restype = None
    try:
        bname = os.path.basename(rfile)
        bname = bname.replace("R$", "")
        restype = bname.replace(".smali", "")
    except:
        pass
    return restype

def update_one_rfile(pubdict, rfile):
    '''更新R文件的ID'''
    #Log.out("update rfile : %s" % rfile)
    conlist = []
    f = open(rfile, "r");
    allcontent = f.readlines()
    for c in allcontent:
        conlist.append(c.replace("\n", ""))
    f.close()
    resname = None
    restype = find_type_byfile(rfile)
    oid = None
    nid = None
    modify = False
    for index in range(len(conlist)):
        c = conlist[index]
        if (c.startswith(".field public static")):
            s = c.split(r" ")
            try:
                resname = s[4].split(":")[0]
                oid = s[6]
                nid = pubdict["%s#%s" % (resname, restype)]
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
    '''更新包含R文件的文件夹'''
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
    Log.out("")

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
            resname = item.get("name")
            restype = item.get("type")
            pubdict["%s#%s" % (resname, restype)] = item.get("id")
    return pubdict

if __name__ == "__main__":
    update_all_rfile(sys.argv[1])