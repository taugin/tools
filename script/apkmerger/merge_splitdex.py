#!/usr/bin/python
# coding: UTF-8


import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)
import Log
import Utils
import Common
import xml.etree.ElementTree as ET

def parse_class(line):
    '''解析类名'''
    if not line.startswith(".class"):
        Log.out("line parse error. not startswith .class : " + line)
        return None
    blocks = line.split()
    return blocks[len(blocks) - 1]

def parse_method_default(className, line):
    '''解析默认方法名'''
    if not line.startswith(".method"):
        Log.out("the line parse error in parse_method_default:" + line)
        return None

    blocks = line.split()
    return className + "->" + blocks[len(blocks) - 1]

def parse_method_invoke(line):
    '''解析方法调用'''
    if not line.startswith("invoke-"):
        Log.out("the line parse error in parse_method_invoke:" + line)

    blocks = line.split()
    return blocks[len(blocks) - 1]

def get_smali_method_count(smaliFile, allMethods):
    '''获取smali文件的方法数'''
    if not os.path.exists(smaliFile):
        return 0

    f = open(smaliFile, 'r', encoding='UTF-8')
    lines = f.readlines()
    f.close()

    classLine = lines[0]
    classLine.strip()
    if not classLine.startswith(".class"):
        Log.out(f + " not startswith .class")
        return 0

    className = parse_class(classLine)
    count = 0
    for line in lines:
        line = line.strip()
        method = None
        if line.startswith(".method"):
            method = parse_method_default(className, line)
        elif line.startswith("invoke-"):
            method = parse_method_invoke(line)

        if method is None:
            continue

        if method not in allMethods:
            count = count + 1
            allMethods.append(method)
        else:
            pass

    return count

def has_special_prefix(file, prefix):
    for p in prefix:
        if (p in file):
            return True
    return False

def add_prefix_files_to_front(allFiles, prefix):
    '''将指定前缀的文件放到前面'''
    if (prefix == None or len(prefix) <= 0):
        return allFiles

    headFiles = []
    tailFiles = []
    for f in allFiles:
        contain = has_special_prefix(f, prefix)
        if (contain):
            headFiles.append(f)
        else:
            tailFiles.append(f)
    allFiles = headFiles + tailFiles;
    return allFiles

def split_dex_detail(masterfolder, smaliFrom, smaliTo, allFiles):
    if (not os.path.exists(os.path.join(masterfolder, smaliFrom))):
        return
    maxFuncNum = 65535
    allRefs = []
    fucNumSum = 0
    handled = 0
    handledFile = None
    finalFunNum = 0

    for f in allFiles:
        if not f.endswith(".smali"):
            continue

        #当函数总数没有达到最大值时，继续遍历
        if fucNumSum < maxFuncNum:
            Log.showNoReturn("[Logging...] 正在处理分包 : [%s : %s]" % (fucNumSum, maxFuncNum))
            thisFucNum = get_smali_method_count(f, allRefs)
            fucNumSum = fucNumSum + thisFucNum
            if fucNumSum < maxFuncNum:
                continue
            else:
                finalFunNum = fucNumSum - thisFucNum

        Log.showNoReturn("[Logging...] 累计函数总数 : [%s : %s]" % (smaliFrom, finalFunNum))
        newDexPath = os.path.join(masterfolder, smaliTo)
        if (not os.path.exists(newDexPath)):
            os.makedirs(newDexPath)
        handledFile = f
        fromSmaliPath = os.path.join(masterfolder, smaliFrom)
        toSmaliPath = os.path.join(masterfolder, smaliTo)
        targetPath = os.path.normpath(f.replace(fromSmaliPath, toSmaliPath))
        Utils.movefile(f, targetPath)

        handled = handled + 1
        if (handledFile != None):
            handledFile = handledFile.replace(masterfolder, "");
            Log.showNoReturn("[Logging...] 已处理文件数 : %s, %s" % (handled, finalFunNum))
            handledFile = None

def find_app_name_path(masterfolder):
    if (os.path.exists(masterfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % masterfolder, True)
        return None
    manifestfile = "%s/AndroidManifest.xml" % masterfolder;
    if (os.path.exists(manifestfile) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % manifestfile, True)
        return None
    ET.register_namespace('android', Common.XML_NAMESPACE)
    manifesttree = ET.parse(manifestfile)
    if (manifesttree == None):
        return None
    manifestroot = manifesttree.getroot()
    if (manifestroot == None):
        return None
    pkgname = manifestroot.get("package")
    application = manifestroot.find("application")
    if (application == None):
        return None
    appname = application.get("{%s}name" % Common.XML_NAMESPACE)
    if (appname == None):
        return None
    if (appname.startswith(".")):
        appname = pkgname + appname
    app_name_path = None
    if (appname != None):
        app_name_path = appname.replace(".", os.sep)
    return app_name_path

def split_dex(masterfolder):
    Log.out("[Logging...] 开始进行分包 ");
    masterfolder = os.path.normpath(masterfolder)
    smaliPath1 = os.path.join(masterfolder, "smali")
    smaliPath2 = os.path.join(masterfolder, "smali_classes2")

    pathlist = []

    app_name_path = find_app_name_path(masterfolder)
    if (app_name_path != None):
        pathlist.append(app_name_path)
    multi_path = "android.support.multidex".replace(".", os.sep)
    pathlist.append(multi_path)

    #分割smali文件夹
    allFiles1 = Utils.list_files(smaliPath1)
    allFiles1.sort()
    allFiles1 = add_prefix_files_to_front(allFiles1, pathlist)
    split_dex_detail(masterfolder, "smali", "smali_classes2", allFiles1)

    #分割smali_classes2文件夹
    allFiles2 = Utils.list_files(smaliPath2)
    split_dex_detail(masterfolder, "smali_classes2", "smali_classes3", allFiles2)
    Log.out("[Logging...] 分包处理完成\n")

if __name__ == "__main__":
    split_dex("F:\\temp\\com.easybrain.sudoku.android-bak\\")
