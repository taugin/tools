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

import subprocess
import zipfile

#编译apk
def apk_compile(folder, compileapk):
    thisdir = os.path.dirname(sys.argv[0])
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "b", folder, "-o", compileapk]
    Log.out("[Logging...] 回编文件名称 : [%s]" % compileapk)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] 回编文件失败")
        return False
    else:
        Log.out("[Logging...] 回编文件成功\n")
        return True

#反编译apk
def apk_decompile(apkfile, decompiled_folder=None):
    if (decompiled_folder == None):
        (name, ext) = os.path.splitext(apkfile)
        decompiled_folder = name
    if (not os.path.exists(decompiled_folder)):
        os.makedirs(decompiled_folder)

    #cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-s", "-f" , apkfile, "-o", decompiled_folder]
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, "d", "-f" , apkfile, "-o", decompiled_folder]
    Log.out("[Logging...] 反编文件名称 : [%s]" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] 反编文件失败")
        return False
    else:
        Log.out("[Logging...] 反编文件成功\n")
        return True

def baksmali(dexfile, outdir):
    Log.out("[Logging...] 开始转换DEX")
    cmdlist = [Common.JAVA, "-jar", Common.BAKSMALI_JAR, "-o", outdir, dexfile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] DEX转换失败\n")
        return False
    else:
        Log.out("[Logging...] DEX转换成功\n")
        return True

#删除APK原有的签名文件
def deletemetainf(src_apk):
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
    Log.out("[Signing...] 执行签名 : %s -> %s" % (os.path.basename(src_apk), os.path.basename(dst_apk)), True)
    if (keystoreinfo == None):
        Log.out ("[Logging...] 签名信息 : [testkey.x509.pem], [testkey.pk8]", True)
        retcode = subprocess.call([Common.JAVA, "-jar", Common.SIGNAPK_JAR, Common.X509, Common.PK8, src_apk, dst_apk], stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 签名成功 : %s" % dst_apk, True)
        else:
            Log.out("[Signing...] 签名失败", True)
    else:
        cmdlist = []
        cmdlist.append(Common.JARSIGNER)

        cmdlist.append("-digestalg")
        cmdlist.append("SHA1")
        cmdlist.append("-sigalg")
        cmdlist.append("MD5withRSA")
        
        cmdlist.append("-keystore")
        cmdlist.append(dir + Common.SEPERATER + keystoreinfo["keystore"])
        cmdlist.append("-storepass")
        cmdlist.append(keystoreinfo["storepass"])
        cmdlist.append("-keypass")
        cmdlist.append(keystoreinfo["keypass"])
        cmdlist.append("-signedjar")
        cmdlist.append(dst_apk)
        cmdlist.append(src_apk)
        cmdlist.append(keystoreinfo["alias"])
        retcode = subprocess.call(cmdlist, stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 签名成功 : %s" % dst_apk, True)
        else:
            Log.out("[Signing...] 签名失败", True)
    Log.out("", True)

#apk对齐
def alignapk(unalignapk, finalapk):
    Log.out("[Logging...] 正在对齐APK", True)
    cmdlist = [Common.ZIPALIGN, "-f", "4", unalignapk, finalapk]
    subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] APK对齐成功\n")
    return True