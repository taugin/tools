#!/usr/bin/python
# coding: UTF-8

import moduleconfig
import Common
import Log
import Utils

import os
import subprocess
import zipfile

#编译apk
def apk_compile(folder, compileapk):
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

#反编译apk
def apk_decompile(apkfile, decompiled_folder=None):
    if (decompiled_folder == None):
        (name, ) = os.path.splitext(apkfile)
        decompiled_folder = name
    if (not os.path.exists(decompiled_folder)):
        os.makedirs(decompiled_folder)

    #cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-s", "-f" , apkfile, "-o", decompiled_folder]
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-f" , apkfile, "-o", decompiled_folder]
    Log.out("[Logging...] 反编文件名称 : [%s]" % Utils.normalPath(apkfile))
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 反编文件失败")
        return False
    else:
        Log.out("[Logging...] 反编文件成功\n")
        return True

def baksmali(dexfile, outdir):
    '''dex文件转smali文件，并且输出到outdir'''
    Log.out("[Logging...] 开始转换文件 : [%s] --> [%s]" % (dexfile, outdir))
    cmdlist = [Common.JAVA, "-jar", Common.BAKSMALI_JAR, "-o", outdir, dexfile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 文件转换失败")
        return False
    else:
        Log.out("[Logging...] 文件转换成功")
        return True

def deletemetainf(src_apk):
    '''删除APK原有的签名文件'''
    signfilelist = []
    z = zipfile.ZipFile(src_apk, "r")
    for file in z.namelist():
        if (file.startswith("META-INF")):
            signfilelist.append(file)
    z.close()
    output = ""
    for l in signfilelist:
        output += "["
        output += l
        output += "]"
        output += " "
    if (output != "") :
        Log.out("[Logging...] 正在删除 : %s" % output, True)
        subprocess.call([Common.AAPT_BIN, "r", src_apk] + signfilelist)

#为APK签名
def signapk(src_apk, dst_apk, keystoreinfo = None):
    deletemetainf(src_apk)
    Log.out("[Signing...] 安卓文件签名 : [%s -> %s]" % (os.path.basename(src_apk), os.path.basename(dst_apk)), True)
    if (keystoreinfo == None):
        Log.out ("[Logging...] 签名文件信息 : [testkey.x509.pem], [testkey.pk8]", True)
        retcode = subprocess.call([Common.JAVA, "-jar", Common.SIGNAPK_JAR, Common.X509, Common.PK8, src_apk, dst_apk], stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 安卓签名成功 : %s" % dst_apk, True)
        else:
            Log.out("[Signing...] 安卓签名失败", True)
    else:
        cmdlist = []
        cmdlist.append(Common.JARSIGNER)

        cmdlist.append("-digestalg")
        cmdlist.append("SHA1")
        cmdlist.append("-sigalg")
        cmdlist.append("MD5withRSA")

        cmdlist.append("-keystore")
        cmdlist.append(os.path.join(Common.PACK_HOME, keystoreinfo["keystore"]))
        cmdlist.append("-storepass")
        cmdlist.append(keystoreinfo["storepass"])
        cmdlist.append("-keypass")
        cmdlist.append(keystoreinfo["keypass"])
        cmdlist.append("-signedjar")
        cmdlist.append(dst_apk)
        cmdlist.append(src_apk)
        cmdlist.append(keystoreinfo["alias"])
        Log.out ("[Logging...] 签名文件信息 : [%s]" % Utils.normalPath(keystoreinfo["keystore"]), True)
        retcode = subprocess.call(cmdlist, stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 安卓签名成功 : [%s]" % dst_apk, True)
        else:
            Log.out("[Signing...] 安卓签名失败", True)
    Log.out("", True)

#apk对齐
def alignapk(unalignapk, finalapk):
    Log.out("[Logging...] 正在对齐文件 : [%s]" % finalapk, True)
    cmdlist = [Common.ZIPALIGN, "-f", "4", unalignapk, finalapk]
    subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 文件对齐成功\n")
    return True

#写developer_config.properties文件
def writeProperties(decompiledfolder, properties):
    if (len(properties) <= 0):
        return
    propertiesFile = os.path.join(decompiledfolder, "assets", "developer_config.properties")
    Log.out("[Logging...] 写入配置文件 : [%s]\n" % propertiesFile)
    plist = []
    for p in properties:
        plist += p["name"] + "=" + p["value"] + "\n"
    pstring = "".join(plist)
    f = open(propertiesFile, "w")
    f.write(pstring)
    f.close()

def jar2dex(jarfile, dexfile):
    Log.out("[Logging...] Jar转换为DEX : [%s -> %s]" % (jarfile, dexfile), True)
    cmdlist = [Common.JAVA, "-jar", Common.DX_JAR, "--dex", "--output=%s" % dexfile, jarfile]
    subprocess.call(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Log.out("[Logging...] Jar转换完成", True)

def clearDupSmali(decompiledfolder):
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