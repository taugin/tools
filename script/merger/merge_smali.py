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
import Utils
import random
import subprocess

def copy_smali(masterfolder, slavefolder):
    smalidirs = ["smali", "smali_classes2", "smali_classes3", "smali_classes4", "smali_classes5", "smali_classes6", "smali_classes7", "smali_classes8", "smali_classes9", "smali_classes10"]

    for smalifrom in smalidirs:
        fromdir = os.path.join(slavefolder, smalifrom)
        if not os.path.exists(fromdir):
            break
        for smalidst in smalidirs:
            dstdir = os.path.join(masterfolder, smalidst)
            if not os.path.exists(dstdir):
                Log.out("[Logging...] 复制汇编文件 : [%s] -> [%s]" % (os.path.basename(fromdir), os.path.basename(dstdir)))
                Utils.copydir(fromdir, dstdir, False)
                break;

def clear_dup_smali(masterfolder):
    Log.out("[Logging...] 清除重复文件 ", True)
    smali = os.path.join(masterfolder, "smali")
    smalidirs = ["smali_classes2", "smali_classes3", "smali_classes4", "smali_classes5", "smali_classes6", "smali_classes7", "smali_classes8", "smali_classes9", "smali_classes10"]
    for smalidir in smalidirs:
        smalidst = os.path.join(masterfolder, smalidir)
        if (not os.path.exists(smalidst)):
            break
        srclist = os.walk(smali, True)
        for root, filedir, files in srclist:
            for file in files:
                file = os.path.join(root, file)
                toDeleteFile = file.replace(smali, smalidst)
                if os.path.exists(toDeleteFile):
                    os.remove(toDeleteFile)
                    Utils.deleteEmptyDir(toDeleteFile)
    Log.out("[Logging...] 清除文件完成\n ", True)

def jar2dex(jarfile, dexfile):
    Log.out("[Logging...] Jar转换为DEX : [%s -> %s]" % (jarfile, dexfile), True)
    cmdlist = [Common.JAVA(), "-jar", Common.DX_JAR, "--dex", "--output=%s" % dexfile, jarfile]
    subprocess.call(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Log.out("[Logging...] Jar转换完成 ", True)

def smali2dex(smalidir, dexfile):
    '''smali文件转dex文件'''
    smalidir = os.path.normpath(smalidir)
    dexfile = os.path.normpath(dexfile)
    Log.out("[Logging...] 开始转换文件 : [%s] --> [%s]" % (smalidir, dexfile))
    cmdlist = [Common.JAVA(), "-jar", Common.SMALI_JAR, "a", "-o", dexfile, smalidir]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 文件转换失败")
        return False
    else:
        Log.out("[Logging...] 文件转换成功")
        return True

def baksmali(dexfile, outdir):
    '''dex文件转smali文件，并且输出到outdir'''
    dexfile = os.path.normpath(dexfile)
    outdir = os.path.normpath(outdir)
    Log.out("[Logging...] 开始转换文件 : [%s] --> [%s]" % (dexfile, outdir))
    tmpdir = os.path.join(os.getcwd(), "tmp%s" % random.randint(0, 1000))
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    cmdlist = [Common.JAVA(), "-jar", Common.BAKSMALI_JAR, "d", "-o", tmpdir, dexfile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    Utils.copydir(tmpdir, outdir, False)
    Utils.deletedir(tmpdir)
    if (ret != 0):
        Log.out("[Logging...] 文件转换失败")
        return False
    else:
        Log.out("[Logging...] 文件转换成功")
        return True

def support_multidex(masterfolder):
    '''增加多dex支持'''
    smaliPath = os.path.join(masterfolder, "smali/")
    multidexFilePath = os.path.join(smaliPath, "android/support/multidex/MultiDex.smali")
    multidexFilePath = os.path.normpath(multidexFilePath)
    if not os.path.exists(multidexFilePath):
        multiDexJar = os.path.join(Common.LIB_DIR, "android-support-multidex.jar")
        if not os.path.exists(multiDexJar):
            Log.out("the method num expired of dex, but no android-support-multidex.jar found")
            return
        multiDexPath = os.path.join(os.getcwd(), "multidex")
        if not os.path.exists(multiDexPath):
            os.makedirs(multiDexPath)
        multiDexFile = os.path.join(multiDexPath, "classes.dex")
        jar2dex(multiDexJar, multiDexFile)
        smaliPath = os.path.join(masterfolder, "smali/");
        baksmali(multiDexFile, smaliPath)
        Utils.deletedir(multiDexPath)

def merge_smali(masterfolder, slavefolder):
    copy_smali(masterfolder, slavefolder)
    support_multidex(masterfolder)
    Log.out("")

if __name__ == "__main__":
    pass
