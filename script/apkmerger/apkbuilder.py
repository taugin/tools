#!/usr/bin/python
# coding: UTF-8
import sys
import os

import Common
import Log
import Utils
import random
import subprocess

def apk_compile(folder, compileapk):
    thisdir = os.path.dirname(sys.argv[0])
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "b", folder, "-o", compileapk]
    Log.out("[Logging...] 回编文件名称 : [%s]" % compileapk)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 回编文件失败")
        return False
    else:
        Log.out("[Logging...] 回编文件成功\n")
        return True

def apk_decompile(apkfile, decompiled_folder=None):
    if (decompiled_folder == None):
        (name, ext) = os.path.splitext(apkfile)
        decompiled_folder = name

    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-f" , apkfile, "-o", decompiled_folder]
    Log.out("[Logging...] 反编文件名称 : [%s]" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 反编文件失败")
        return False
    else:
        Log.out("[Logging...] 反编文件成功\n")
        return True

def copy_smali(masterfolder, slavefolder):
    Log.out("[Logging...] 复制汇编文件 ")

    fromdir = "%s/smali" % slavefolder
    dstdir = "%s/smali_classes2" % masterfolder
    if (os.path.exists(fromdir)):
        Utils.copydir(fromdir, dstdir, False)

    fromdir = "%s/smali_classes2" % slavefolder
    dstdir = "%s/smali_classes3" % masterfolder
    if (os.path.exists(fromdir)):
        Utils.copydir(fromdir, dstdir, False)

    support_multidex(masterfolder)
    update_google_ad(masterfolder)
    clear_dup_smali(masterfolder)

def update_google_ad(decompiledfolder):
    Log.out("[Logging...] 更新谷歌广告")
    smali = os.path.join(decompiledfolder, "smali")
    smali2 = os.path.join(decompiledfolder, "smali_classes2")
    if (not os.path.exists(smali2)):
        return
    srclist = os.walk(smali2, True)
    for root, filedir, files in srclist:
        for file in files:
            fromfile = os.path.join(root, file)
            tofile = fromfile.replace(smali2, smali);
            if (os.path.exists(tofile)):
                Utils.copyfile(fromfile, tofile, True)
                Utils.deleteFile(fromfile)

#apk对齐
def alignapk(unalignapk, finalapk):
    finalapk = os.path.normpath(finalapk)
    Log.out("[Logging...] 正在对齐文件 : [%s]" % finalapk, True)
    cmdlist = [Common.ZIPALIGN, "-f", "4", unalignapk, finalapk]
    subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 文件对齐成功\n")
    return True

def clear_dup_smali(decompiledfolder):
    smali = os.path.join(decompiledfolder, "smali")
    smali2 = os.path.join(decompiledfolder, "smali_classes2")
    if (not os.path.exists(smali2)):
        return
    Log.out("[Logging...] 清除重复文件 ", True)
    srclist = os.walk(smali, True)
    for root, filedir, files in srclist:
        for file in files:
            file = os.path.join(root, file)
            if True or r"com\abch\sdk" in file:
                toDeleteFile = file.replace(smali, smali2)
                if os.path.exists(toDeleteFile):
                    os.remove(toDeleteFile)
                    Utils.deleteEmptyDir(toDeleteFile)
    Log.out("[Logging...] 清除文件完成\n ", True)

def jar2dex(jarfile, dexfile):
    Log.out("[Logging...] Jar转换为DEX : [%s -> %s]" % (jarfile, dexfile), True)
    cmdlist = [Common.JAVA, "-jar", Common.DX_JAR, "--dex", "--output=%s" % dexfile, jarfile]
    subprocess.call(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Log.out("[Logging...] Jar转换完成 ", True)

def baksmali(dexfile, outdir):
    '''dex文件转smali文件，并且输出到outdir'''
    dexfile = os.path.normpath(dexfile)
    outdir = os.path.normpath(outdir)
    Log.out("[Logging...] 开始转换文件 : [%s] --> [%s]" % (dexfile, outdir))
    tmpdir = os.path.join(os.getcwd(), "tmp%s" % random.randint(0, 1000))
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    cmdlist = [Common.JAVA, "-jar", Common.BAKSMALI_JAR, "-o", tmpdir, dexfile]
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

def support_multidex(decompiledfolder):
    smaliPath = os.path.join(decompiledfolder, "smali/")
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
        smaliPath = os.path.join(decompiledfolder, "smali/");
        baksmali(multiDexFile, smaliPath)
        Utils.deletedir(multiDexPath)
