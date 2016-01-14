#!/usr/bin/python
# coding: UTF-8
import os
import sys
import getopt
import platform
import zipfile
import subprocess;

SEPERATER = os.path.sep
KEYTOOL = "keytool"
JARSIGNER="jarsigner"
JDK7ARG="-tsa https://timestamp.geotrust.com/tsa -digestalg SHA1 -sigalg MD5withRSA"
USE_TESTSIGN_FILE = False

def log(str, show=False):
    if (show):
        print(str)

def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        log("操作完成，按任意键退出", True)
        msvcrt.getch()

def inputvalue(prompt, max) :
    while True:
        p = input(prompt)
        if (p.isdigit()):
            if (int(p) >= 1 and int(p) <= max):
                return p
    
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
        log("[Logging...] 正在删除 : %s" % output, True)
        subprocess.call(["aapt", "r", src_apk] + signfilelist)

def sign_apk(src_apk, dst_apk, keystoreinfo):
    deletemetainf(src_apk)
    log("[Signing...] 执行签名 : %s -> %s" % (os.path.basename(src_apk), os.path.basename(dst_apk)), True)
    if (len(keystoreinfo) <= 0):
        log ("[Logging...] 签名信息 : [testkey.x509.pem], [testkey.pk8]", True)
        #deletemetainf "$1"
        toodir = os.path.dirname(sys.argv[0])
        signapk_jar = toodir + SEPERATER + "signapk.jar"
        x509 = toodir + SEPERATER + "testkey.x509.pem"
        pk8 = toodir + SEPERATER + "testkey.pk8"
        retcode = subprocess.call(["java", "-jar", signapk_jar, x509, pk8, src_apk, dst_apk], stdout=subprocess.PIPE)
        if (retcode == 0):
            log("[Signing...] 签名成功 : %s" % dst_apk, True)
        else:
            log("[Signing...] 签名失败", True)
            pause()
    else:
        log("[Logging...] 签名信息 : keystore : [%s], storepass : [%s] , keyalias : [%s], keypass : [%s]" % (keystoreinfo[0],keystoreinfo[1], keystoreinfo[2], keystoreinfo[3]), True)

        dir = os.path.dirname(src_apk)
        cmdlist = []
        cmdlist.append(JARSIGNER)

        #cmdlist +=["-tsa", "https://timestamp.geotrust.com/tsa"]
        cmdlist.append("-digestalg")
        cmdlist.append("SHA1")
        cmdlist.append("-sigalg")
        cmdlist.append("MD5withRSA")
        
        cmdlist.append("-keystore")
        cmdlist.append(dir + SEPERATER + keystoreinfo[0])
        cmdlist.append("-storepass")
        cmdlist.append(keystoreinfo[1])
        cmdlist.append("-keypass")
        cmdlist.append(keystoreinfo[3])
        cmdlist.append("-signedjar")
        cmdlist.append(dst_apk)
        cmdlist.append(src_apk)
        cmdlist.append(keystoreinfo[2])
        retcode = subprocess.call(cmdlist, stdout=subprocess.PIPE)
        if (retcode == 0):
            log("[Signing...] 签名成功 : %s" % dst_apk, True)
        else:
            log("[Signing...] 签名失败", True)
            pause()
    log("---------------------------------------", True);

def exec_sign_process(src_apk, USE_TESTSIGN_FILE):
    log("[Logging...] APK 文件 : " + src_apk, True)
    index = src_apk.rfind(".apk")
    if (index == -1):
        log("[Error...] 无法识别的的apk压缩包 : %s" % src_apk, True)
        return
    log("index : %d " % index)
    log("substring : %s " % src_apk[0:index])
    dst_apk = src_apk[0:index] + "-signed.apk"
    log("dst_apk : %s " % dst_apk)
    keystoreinfo = []
    if(USE_TESTSIGN_FILE == False):
        keystoreinfo = readkeystore(os.path.dirname(src_apk))
    sign_apk(src_apk, dst_apk, keystoreinfo)

def readkeystore(dir):
    listfile=os.listdir(dir)
    storefiles = []
    #log(listfile)
    index = 0
    storeindex = 0
    for file in listfile:
        if(file.rfind(".keystore") != -1):
            storefiles.append(file)
            storeindex+=1
        index+=1
    if (storeindex > 1):
        index = 1
        for keyfile in storefiles:
            log("             [%d] : %s" %(index, keyfile), True)
            index += 1
        p = inputvalue("[Logging...] 输入索引 : ", storeindex)
    else:
        p = 0
    if (storeindex <= 0):
        log("[Logging...] 找不到签名文件", True)
        sys.exit()
    keystorefile = storefiles[int(p) - 1]
    log("[Logging...] 签名文件 : %s" % keystorefile, True)
    index = keystorefile.rfind(".keystore")
    filename = keystorefile[0:index]
    splits = filename.split("_")
    if (len(splits) < 3):
        log("[Logging...] 无法获取签名文件信息,请重命名签名文件格式 <alias_pwd_123456.keystore>", True)
        sys.exit()
    keystorealias = splits[0]
    keystorepass = splits[2]
    keyaliaspass = splits[2]

    if (keystorealias == "" or keystorepass == ""):
        log("[Error...] keystorealias or keystorepass is empty")
        sys.exit()

    retcode = subprocess.call([KEYTOOL, "-list", "-keystore", dir + SEPERATER + keystorefile, "-storepass", keystorepass], stdout=subprocess.PIPE)
    if (retcode != 0):
        log("[Logging...] 签名文件不正确", True)
        sys.exit()
    keystoreinfo = []
    keystoreinfo.append(keystorefile)
    keystoreinfo.append(keystorepass)
    keystoreinfo.append(keystorealias)
    keystoreinfo.append(keyaliaspass)
    return keystoreinfo

if (len(sys.argv) < 2):
    log("[Logging...] 缺少参数, %s [-t] <src_apk>" % os.path.basename(sys.argv[0]), True);
    sys.exit()
opts, args = getopt.getopt(sys.argv[1:], "t")
for op, value in opts:
    if (op == "-t"):
        USE_TESTSIGN_FILE = True

for file in args :
    if (os.path.isdir(file)):
        listfiles = os.listdir(file)
        for apkfile in listfiles :
            apkpath = file + SEPERATER + apkfile
            if (len(apkpath) >= 4 and apkpath[-4:] == ".apk"):
                exec_sign_process(os.path.abspath(apkpath), USE_TESTSIGN_FILE)
    else:
        if (len(file) >= 4 and file[-4:] == ".apk"):
            exec_sign_process(os.path.abspath(file), USE_TESTSIGN_FILE)