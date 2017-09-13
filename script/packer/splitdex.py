#!/usr/bin/python
# coding: UTF-8


import moduleconfig
import Common
import Log
import Utils

import os
import apkbuilder

def parse_class(line):
    if not line.startswith(".class"):
        Log.out("line parse error. not startswith .class : " + line)
        return None
    blocks = line.split()
    return blocks[len(blocks) - 1]

def parse_method_default(className, line):
    if not line.startswith(".method"):
        Log.out("the line parse error in parse_method_default:" + line)
        return None

    blocks = line.split()
    return className + "->" + blocks[len(blocks) - 1]

def parse_method_invoke(line):
    if not line.startswith("invoke-"):
        Log.out("the line parse error in parse_method_invoke:" + line)

    blocks = line.split()
    return blocks[len(blocks) - 1]

def get_smali_method_count(smaliFile, allMethods):
    if not os.path.exists(smaliFile):
        return 0
    
    f = open(smaliFile)
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

        # log_utils.debug("the method is "+method)

        if method not in allMethods:
            count = count + 1
            allMethods.append(method)
        else:
            pass
            # log_utils.debug(method + " is already exists in allMethods.")

    return count

def split_dex(decompiledfolder):
    Log.out("[Logging...] 开始进行分包 ");
    smaliPath = os.path.join(decompiledfolder, "smali/")
    multidexFilePath = os.path.join(smaliPath, "android/support/multidex/MultiDex.smali")
    multidexFilePath = os.path.normpath(multidexFilePath)
    if not os.path.exists(multidexFilePath):
        multiDexJar = os.path.join(Common.LIB_DIR, "android-support-multidex.jar")
        if not os.path.exists(multiDexJar):
            Log.out("the method num expired of dex, but no android-support-multidex.jar found")
            return
        multiDexPath = os.path.join(Common.WORKSPACE, "multidex")
        if not os.path.exists(multiDexPath):
            os.makedirs(multiDexPath)
        multiDexFile = os.path.join(multiDexPath, "classes.dex")
        apkbuilder.jar2dex(multiDexJar, multiDexFile)
        smaliPath = os.path.join(decompiledfolder, "smali/");
        apkbuilder.baksmali(multiDexFile, smaliPath)

    maxFuncNum = 65535
    currFucNum = 0
    currDexIndex = 1
    allRefs = []

    allFiles = Utils.list_files(os.path.join(decompiledfolder, "smali"))
    allFiles.sort()
    Log.out("allFile1 len : %s" % len(allFiles))
    allFiles = sortFiles(allFiles)
    Log.out("allFile2 len : %s" % len(allFiles))
    #保证U9Application等类在第一个classex.dex文件中
    for f in allFiles:
        f = f.replace("\\", "/")
        if "/com/abch/sdk" in f or "/android/support/multidex" in f:
            currFucNum = currFucNum + get_smali_method_count(f, allRefs)

    totalFucNum = currFucNum

    handled = 0

    handledFile = None
    srcFile = None
    for f in allFiles:
        srcFile = f
        f = f.replace("\\", "/")
        if not f.endswith(".smali"):
            continue
        if "/com/abch/sdk" in f or "/android/support/multidex" in f \
             or "smali_classes" in f:
            continue

        thisFucNum = get_smali_method_count(f, allRefs)
        totalFucNum = totalFucNum + thisFucNum

        if currFucNum + thisFucNum >= maxFuncNum:
            currFucNum = thisFucNum
            currDexIndex = currDexIndex + 1
            newDexPath = os.path.join(decompiledfolder, "smali_classes"+str(currDexIndex))
            if (not os.path.exists(newDexPath)):
                os.makedirs(newDexPath)
        else:
            currFucNum = currFucNum + thisFucNum

        if currDexIndex > 1:
            handledFile = srcFile
            smaliClass = "smali_classes"+str(currDexIndex)
            pkgFilePath = f[len(smaliPath):]
            targetPath = os.path.normpath(os.path.join(decompiledfolder, smaliClass, pkgFilePath))
            Utils.copyfile(srcFile, targetPath)
            Utils.deleteFile(srcFile)

        handled = handled + 1
        if (handledFile != None):
            handledFile = handledFile.replace(decompiledfolder, "");
        Log.showNoReturn("[Logging...] 已处理文件数 : %s, %s, %s, %s" % (handled, totalFucNum, currFucNum + thisFucNum, handledFile))
    Log.out("[Logging...] 分包处理完成\n")

def sortFiles(allFiles):
    comFiles = []
    for file in allFiles:
        if "smali\com" in file and "com\ninemgames" not in file:
            comFiles.append(file)
            allFiles.remove(file)
    allFiles += comFiles
    return allFiles