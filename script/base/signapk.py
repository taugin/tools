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

import getopt
import platform
import zipfile
import subprocess
import time

USE_TESTSIGN_FILE = False
OUTPUT_SIGNED_APK = None
USE_JARSIGNER = False
ALIGN_APK = False

def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        Log.out("[Logging...] 操作完成，按任意键退出", True)
        msvcrt.getch()

def inputvalue(prompt, max) :
    while True:
        p = input(prompt)
        if (p.isdigit()):
            if (int(p) >= 1 and int(p) <= max):
                return p

def getaabpackagename(file):
    result = None
    try:
        cmdlist = []
        cmdlist.append("java")
        cmdlist.append("-jar")
        cmdlist.append(Common.BUNDLE_TOOL)
        cmdlist.append("dump")
        cmdlist.append("manifest")
        cmdlist.append("--bundle=%s" % file)
        cmdlist.append("--xpath=/manifest/@package")
        #Log.out("cmdlist : %s" % (" ".join(cmdlist)))
        p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)
        result = p.stdout.read()
        result = result.decode().strip()
    except:
        pass
    return result

def getapkpackagename(file):
    result = None
    try :
        cmdlist = [Common.AAPT2_BIN, "d", "badging", file]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)
        alllines = process.stdout.readlines()
        for line in alllines :
            tmp = Utils.parseString(line)
            if (tmp.startswith("package: ")):
                try:
                    tmppkg = tmp[len("package: "):]
                    tmppkg = tmppkg.replace("\r", "")
                    tmppkg = tmppkg.replace("\n", "")
                    tmppkg = tmppkg.replace("'", "")
                    tmpsplit = tmppkg.split(" ")
                    if tmpsplit != None and len(tmpsplit) >= 3:
                        result = tmpsplit[0].split("=")[1]
                        break;
                except:
                    pass
    except:
        pass
    return result

def getpackagename(file):
    name, ext = os.path.splitext(file)
    if (ext == ".apk"):
        return getapkpackagename(file)
    if (ext == ".aab"):
        return getaabpackagename(file)
    return None

def deletemetainf(src_apk):
    signfilelist = []
    z = zipfile.ZipFile(src_apk, "r")
    for file in z.namelist():
        if ((file.startswith("META-INF") and (file.endswith(".RSA") or file.endswith(".SF") or file.endswith(".MF")))):
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

def signapk_with_jarsigner(src_apk, tmp_apk, aligned_apk, dst_apk, keystoreinfo):
    Log.out("")
    alignapk(src_apk, tmp_apk)
    if not os.path.exists(tmp_apk):
        tmp_apk = src_apk
    deletemetainf(tmp_apk)
    Log.out("[Signing...] 执行签名 : %s -> %s" % (os.path.basename(tmp_apk), os.path.basename(dst_apk)), True)
    if (len(keystoreinfo) <= 0):
        Log.out ("[Logging...] 签名信息 : [testkey.x509.pem], [testkey.pk8]", True)
        #deletemetainf "$1"
        retcode = subprocess.call([Common.JAVA, "-jar", Common.SIGNAPK_JAR, Common.X509, Common.PK8, tmp_apk, dst_apk], stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 签名成功 : %s" % dst_apk, True)
        else:
            Log.out("[Signing...] 签名失败", True)
            pause()
    else:
        if Common.JARSIGNER == None or len(Common.JARSIGNER) < 0 or not os.path.exists(Common.JARSIGNER):
            Log.out("[Signing...] 签名失败 : 无法找到签名文件 [jarsigner]", True)
            return
        Log.out("[Logging...] 签名信息 : [jarsigner] keystore : [%s], storepass : [%s] , keyalias : [%s], keypass : [%s]" % (os.path.basename(keystoreinfo[0]),keystoreinfo[1], keystoreinfo[2], keystoreinfo[3]), True)

        dir = os.path.dirname(src_apk)
        cmdlist = []
        cmdlist.append(Common.JARSIGNER)

        cmdlist.append("-digestalg")
        cmdlist.append("SHA-256")
        cmdlist.append("-sigalg")
        cmdlist.append("SHA256withRSA")
        
        cmdlist.append("-keystore")
        cmdlist.append(keystoreinfo[0])
        cmdlist.append("-storepass")
        cmdlist.append(keystoreinfo[1])
        cmdlist.append("-keypass")
        cmdlist.append(keystoreinfo[3])
        cmdlist.append("-signedjar")
        cmdlist.append(dst_apk)
        cmdlist.append(tmp_apk)
        cmdlist.append(keystoreinfo[2])
        Utils.printExecCmdString(cmdlist)
        retcode = subprocess.call(cmdlist, stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 签名成功 : %s" % dst_apk, True)
        else:
            Log.out("[Signing...] 签名失败", True)
            pause()
    Log.out("", True);

def signapk_with_apksigner(src_apk, tmp_apk, aligned_apk, dst_apk, keystoreinfo):
    Log.out("")
    Utils.copyfile(src_apk, tmp_apk)
    deletemetainf(tmp_apk)
    alignapk(tmp_apk, aligned_apk)
    Log.out("[Signing...] 执行签名 : %s -> %s" % (os.path.basename(aligned_apk), os.path.basename(dst_apk)), True)
    if (len(keystoreinfo) <= 0):
        Log.out("[Signing...] 签名失败 : 签名文件信息有误", True)
        pause()
    else:
        Log.out("[Logging...] 签名信息 : [apksigner] keystore : [%s], storepass : [%s] , keyalias : [%s], keypass : [%s]" % (os.path.basename(keystoreinfo[0]),keystoreinfo[1], keystoreinfo[2], keystoreinfo[3]), True)
        Log.out("[Logging...] 版本信息 : [%s]" % os.path.basename(Common.APKSIGNER))
        cmdlist = []
        cmdlist.append("java")
        cmdlist.append("-jar")
        cmdlist.append(Common.APKSIGNER)

        cmdlist.append("sign")
        cmdlist.append("--ks")
        cmdlist.append(keystoreinfo[0])
        cmdlist.append("--ks-key-alias")
        cmdlist.append(keystoreinfo[2])
        cmdlist.append("--ks-pass")
        cmdlist.append("pass:" + keystoreinfo[1])
        cmdlist.append("--key-pass")
        cmdlist.append("pass:" + keystoreinfo[3])
        cmdlist.append("--v2-signing-enabled")
        cmdlist.append("true")
        cmdlist.append("--v4-signing-enabled")
        cmdlist.append("false")
        cmdlist.append("--out")
        cmdlist.append(dst_apk)
        cmdlist.append(aligned_apk)
        Utils.printExecCmdString(cmdlist)
        retcode = subprocess.call(cmdlist, stdout=subprocess.PIPE)
        if (retcode == 0):
            Log.out("[Signing...] 签名成功 : %s" % dst_apk, True)
            time.sleep(1)
        else:
            Log.out("[Signing...] 签名失败", True)
            pause()
    Log.out("", True);

def exec_sign_process(src_apk, USE_TESTSIGN_FILE):
    global OUTPUT_SIGNED_APK
    Log.out("[Logging...] APK 文件 : [%s]" % src_apk, True)
    if not os.path.exists(src_apk):
        Log.out("[Logging...] 文件丢失", True)
        return False
    name,ext = os.path.splitext(src_apk)
    if (ext != None):
        ext = ext.lower()
    index = src_apk.rfind(ext)
    if (index == -1):
        Log.out("[Logging...] 无法识别 : [%s]" % src_apk, True)
        return
    #Log.out("index : %d " % index)
    #Log.out("substring : %s " % src_apk[0:index])
    dst_apk = src_apk[0:index] + "-signed" + ext
    if (OUTPUT_SIGNED_APK != None and len(OUTPUT_SIGNED_APK) > 0):
        dst_apk = OUTPUT_SIGNED_APK
    #Log.out("dst_apk : %s " % dst_apk)
    keystoreinfo = []
    if(USE_TESTSIGN_FILE == False):
        keystoreinfo = readkeystore(src_apk, os.path.dirname(src_apk))
    dirname = os.path.dirname(src_apk);
    tmp_name = os.path.basename(src_apk) + "-tmp" + ext
    tmp_apk = os.path.join(dirname, tmp_name)
    aligned_name = os.path.basename(src_apk) + "-aligned" + ext
    aligned_apk = os.path.join(dirname, aligned_name)
    if (USE_JARSIGNER or ext == ".aab"):
        signapk_with_jarsigner(src_apk, tmp_apk, aligned_apk, dst_apk, keystoreinfo)
    else:
        signapk_with_apksigner(src_apk, tmp_apk, aligned_apk, dst_apk, keystoreinfo)
    Utils.deleteFile(tmp_apk)
    Utils.deleteFile(aligned_apk)
    try:
        cmdlist = [Common.ZIPALIGN, "-c", "-v", "4", dst_apk]
        p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
        all_lines = p.stdout.readlines()
        last_line = None
        if len(all_lines) > 0:
            last_line = str(all_lines[-1], "utf-8").strip()
        Log.out("[Logging...] 对齐结果 : [%s]" % last_line)
        if "FAILED" in last_line:
            Common.pause()
    except:
        pass

def readkeystore(src_apk, filedir):
    listfile=os.listdir(filedir)
    storefiles = []
    #Log.out(listfile)
    index = 0
    storeindex = 0
    for file in listfile:
        if(file.rfind(".keystore") != -1 or file.rfind(".jks") != -1):
            storefiles.append(file)
            storeindex+=1
        index+=1
    ###########################################
    if (len(storefiles) <= 0):
        packagename = getpackagename(src_apk)
        if (packagename != None and len(packagename) > 0):
            pkg_storefile = os.path.join(Common.KEYSTORES_DIR, "appsignfiles", packagename)
            if (pkg_storefile != None and os.path.isdir(pkg_storefile)):
                Log.out("[Logging...] 文件包名 : [%s]" % packagename)
                listfile=os.listdir(pkg_storefile)
                #Log.out(listfile)
                index = 0
                storeindex = 0
                for file in listfile:
                    if(file.endswith(".keystore") or file.endswith(".jks")):
                        storefiles.append(os.path.join(pkg_storefile, file))
                        storeindex+=1
                    index+=1
    ###########################################
    if (storeindex > 1):
        index = 1
        for keyfile in storefiles:
            Log.out("             [%d] : %s" %(index, keyfile), True)
            index += 1
        p = inputvalue("[Logging...] 输入索引 : ", storeindex)
    else:
        p = 0
    if (storeindex <= 0):
        Log.out("[Logging...] 读取签名 : 找不到签名文件, 使用默认签名文件", True)
        keystorefile = os.path.normpath(Common.KEYSTORES_DEFAULT_FILE)
    else:
        keystorefile = storefiles[int(p) - 1]
    Log.out("[Logging...] 签名文件 : %s" % keystorefile, True)
    keystorename = os.path.basename(keystorefile)
    index = keystorename.rfind(".keystore")
    if index < 0:
        index = keystorename.rfind(".jks")
    filename = keystorename[0:index]
    splits = filename.split("_")
    if (len(splits) < 3):
        Log.out("[Logging...] 无法获取签名文件信息,请重命名签名文件格式 <[alias]_[storepass]_[aliaspass].keystore/jks>", True)
        sys.exit()
    keystorealias = splits[0]
    if (splits[1] != "pwd"):
        keystorepass = splits[1]
    else:
        keystorepass = splits[2]
    keyaliaspass = splits[2]

    if (keystorealias == "" or keystorepass == ""):
        Log.out("[Logging...] keystorealias or keystorepass is empty")
        sys.exit()

    keystorepath = os.path.normpath(os.path.join(filedir, keystorefile))

    if Common.KEYTOOL == None or len(Common.KEYTOOL) <= 0 or not os.path.exists(Common.KEYTOOL):
        Log.out("[Logging...] 验签失败 : 无法找到签名文件 [keytool]")
    else:
        retcode = subprocess.Popen([Common.KEYTOOL, "-list", "-keystore", keystorepath, "-storepass", keystorepass], stdout=subprocess.PIPE)
        if (retcode.returncode != 0):
            Log.out("[Logging...] 签名错误 : {}".format(Utils.parseString(retcode.stdout.read())), True)
            pause()
            sys.exit()
    keystoreinfo = []
    keystoreinfo.append(keystorepath)
    keystoreinfo.append(keystorepass)
    keystoreinfo.append(keystorealias)
    keystoreinfo.append(keyaliaspass)
    return keystoreinfo

def exec_align_process(src_apk):
    global OUTPUT_SIGNED_APK
    Log.out("[Logging...] APK 文件 : [%s]" % src_apk, True)

    if not os.path.exists(src_apk):
        Log.out("[Logging...] 文件丢失", True)
        return False

    index = src_apk.rfind(".apk")
    if (index == -1):
        Log.out("[Logging...] 无法识别 : [%s]" % src_apk, True)
        return
    dst_apk = src_apk[0:index] + "-aligned.apk"
    if (OUTPUT_SIGNED_APK != None and len(OUTPUT_SIGNED_APK) > 0):
        dst_apk = OUTPUT_SIGNED_APK
    alignapk(src_apk, dst_apk)
    time.sleep(2)

#apk对齐
def alignapk(unalignapk, finalapk):
    finalapk = os.path.normpath(finalapk)
    Log.out("[Logging...] 对齐文件 : [%s]" % finalapk, True)
    cmdlist = [Common.ZIPALIGN, "-p", "-f", "4", unalignapk, finalapk]
    subprocess.call(cmdlist, stdout=subprocess.PIPE)
    try:
        cmdlist = [Common.ZIPALIGN, "-c", "-v", "4", finalapk]
        p = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
        all_lines = p.stdout.readlines()
        last_line = None
        if len(all_lines) > 0:
            last_line = str(all_lines[-1], "utf-8").strip()
        Log.out("[Logging...] 对齐结果 : [%s]" % last_line)
        if "FAILED" in last_line:
            Common.pause()
    except:
        pass
    Log.out("\n")
    return True

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        Log.out("[Logging...] 脚本缺少参数 : %s [-t] <src_apk>, [-a] 对齐apk" % os.path.basename(sys.argv[0]), True);
        sys.exit()
    opts, args = getopt.getopt(sys.argv[1:], "atjo:")
    for op, value in opts:
        if (op == "-t"):
            USE_TESTSIGN_FILE = True
        elif (op == "-o"):
            OUTPUT_SIGNED_APK = value
        elif (op == "-a"):
            ALIGN_APK = True
        elif (op == "-j"):
            USE_JARSIGNER = True
    if (ALIGN_APK == True):
        for file in args :
            if (os.path.isdir(file)):
                listfiles = os.listdir(file)
                for apkfile in listfiles :
                    apkpath = file + Common.SEPERATER + apkfile
                    if (len(apkpath) >= 4 and apkpath[-4:] == ".apk"):
                        exec_align_process(os.path.abspath(apkpath))
            else:
                if (len(file) >= 4 and file[-4:] == ".apk"):
                    exec_align_process(os.path.abspath(file))
    else:
        for file in args :
            if (os.path.isdir(file)):
                listfiles = os.listdir(file)
                for apkfile in listfiles :
                    apkpath = file + Common.SEPERATER + apkfile
                    if (len(apkpath) >= 4 and (apkpath[-4:] == ".apk" or apkpath[-4:] == ".aab")):
                        exec_sign_process(os.path.abspath(apkpath), USE_TESTSIGN_FILE)
            else:
                if (len(file) >= 4 and (file[-4:] == ".apk" or file[-4:] == ".aab")):
                    exec_sign_process(os.path.abspath(file), USE_TESTSIGN_FILE)