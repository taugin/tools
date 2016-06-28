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

import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import shutil
import platform
import getopt

USAGE = "[Logging...] 缺少参数: %s [-e] [-p newpkgname] [-l labelname] <*.apk>" % os.path.basename(sys.argv[0])
MANIFEST_FILE = "AndroidManifest.xml"
TMP_DECOMPILE_FOLDER = "debuild"
TMP_DECOMPILE_APKFILE = "debuild.apk"
APP_ENTRYAPPLICATION = "com.loader.dexloader.WrapperApp"
APP_APPLICATION_KEY = "APPLICATION_CLASS_NAME"
DEX_ENCRYPTDATA = "encryptdata.dat"
DEX_DECRYPTDATA_PATH = os.path.join(TMP_DECOMPILE_FOLDER, "assets", DEX_ENCRYPTDATA)
APP_MODIFIED_MANIFEST = os.path.join(TMP_DECOMPILE_FOLDER, MANIFEST_FILE)
SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "signapk", "signapk.py")
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"
TRY_CONFIG = "modapk.tryagain"

APK_SRCFILE = ""
APK_NEWPKG = ""
APK_NEWLABEL = ""
APK_ENCRYPT = False

#输入参数封装
def inputArguement(prompt):
    return input(prompt)

#暂停参数封装
def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        Log.out("操作完成，按任意键退出", True)
        msvcrt.getch()

#反编译apk
def apk_decompile(apkfile):
    thisdir = os.path.dirname(sys.argv[0])
    cmdlist = ["java", "-jar", Common.APKTOOL_JAR, "d", "-s", "-f" , apkfile, "-o", TMP_DECOMPILE_FOLDER]
    Log.out("[Logging...] 反编译中 %s" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] 反编译出错 ...")
        return False
    else:
        return True

#回编译apk
def apk_compile():
    thisdir = os.path.dirname(sys.argv[0])
    cmdlist = ["java", "-jar", Common.APKTOOL_JAR, "b", TMP_DECOMPILE_FOLDER, "-o", TMP_DECOMPILE_APKFILE]
    Log.out("[Logging...] 回编译中 %s" % TMP_DECOMPILE_APKFILE)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Error...] 回编译出错 ...")
        return False
    else:
        return True

#修改应用程序包名
def modify_packagename_ifneed(root):
    if (APK_NEWPKG != None and APK_NEWPKG != ""):
        Log.out("[Logging...] 修改包名 " + APK_NEWPKG)
        root.set("package", APK_NEWPKG)

#修改应用程序名称
def modify_applabel_ifneed(root):
    if (APK_NEWLABEL != None and APK_NEWLABEL != ""):
        Log.out("[Logging...] 修改名称 " + APK_NEWLABEL)
        application = root.find("application");
        application.set("{%s}label" % XML_NAMESPACE, APK_NEWLABEL)

#增加关于loader的一些信息
def modify_appname_forloader(root):
    # 不加密Apk时直接返回
    if (APK_ENCRYPT == False):
        return

    pkgname = root.get("package")
    application = root.find("application");
    appname = application.get("{%s}name" % XML_NAMESPACE)
    if (appname != None and appname == APP_ENTRYAPPLICATION):
        Log.out("[Logging...] 貌似已经加过密了，查看一下吧")
        return False
    Log.out("[Logging...] 设置入口 Application : %s" % APP_ENTRYAPPLICATION)
    application.set("{%s}name" % XML_NAMESPACE, APP_ENTRYAPPLICATION)
    Log.out("[Logging...] 应用包名 %s" % pkgname)
    if (appname != None):
        fullappname = appname
        if (appname.startswith(".")):
            fullappname = pkgname + appname
        Log.out("[Logging...] 设置真正 Application : %s" % fullappname)
        ET.SubElement(application, 'meta-data android:name="%s" android:value="%s"' % (APP_APPLICATION_KEY, fullappname))

#修改AndroidManifest.xml
def modify_xml():
    Log.out("[Logging...] 正在编辑 AndrodManifest.xml")
    manifest = "%s/AndroidManifest.xml" % TMP_DECOMPILE_FOLDER
    ET.register_namespace('android', XML_NAMESPACE)
    tree = ET.parse(manifest)
    root = tree.getroot()
    modify_appname_forloader(root)
    # Modify package name for apk
    modify_packagename_ifneed(root)
    modify_applabel_ifneed(root);
    tree.write(manifest, encoding='utf-8', xml_declaration=True)
    return True

#复制一份新的apk，以免损坏了原apk
def generate_dstapk(dstapk):
    Log.out("[Logging...] 正在生成 %s" % dstapk)
    shutil.copyfile(srcapkname, dstapk)

#将classes.des压缩为encryptdata.dat
def generate_encryptdata():
    basezf = zipfile.ZipFile(srcapkname, "r")
    zipf = zipfile.ZipFile(DEX_ENCRYPTDATA,"w")
    zipf.writestr("classes.dex", basezf.read("classes.dex"))
    zipf.close()
    basezf.close()
    return DEX_ENCRYPTDATA

#添加壳文件
def addloader(dstapk):
    subprocess.call([Common.AAPT_BIN, "r", dstapk, MANIFEST_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if (APK_ENCRYPT == True):
        subprocess.call([Common.AAPT_BIN, "r", dstapk, "classes.dex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call([Common.AAPT_BIN, "r", dstapk, "assets/%s" % DEX_ENCRYPTDATA], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    szf = zipfile.ZipFile(TMP_DECOMPILE_APKFILE, "r")
    zf = zipfile.ZipFile(dstapk, "a")

    ###############################################################################
    #加密Apk时加入壳classes.dex
    if (APK_ENCRYPT == True):
        #将原classes.dex文件压缩改名后写入assets文件夹
        Log.out("[Logging...] 正在拷贝 assets/%s" % DEX_ENCRYPTDATA)
        encryptdata_file = generate_encryptdata();
        zf.write(encryptdata_file, "assets/%s" % DEX_ENCRYPTDATA, zipfile.ZIP_DEFLATED)

        #将壳classes.dex文件写入
        Log.out("[Logging...] 正在拷贝 %s" % "classes.dex")
        srcclassdex = os.path.join(MODAPK_DIR, "classes.dex")
        zf.write(srcclassdex, "classes.dex")
    ###############################################################################
    #将修改后的AndroidManifest.xml写入
    Log.out("[Logging...] 正在拷贝 %s" % MANIFEST_FILE)
    zf.writestr(MANIFEST_FILE, szf.read(MANIFEST_FILE))

    zf.close()
    szf.close()
    return True

#清除临时文件夹
def clear_tmp_folder():
    Log.out("[Logging...] 清除临时文件")
    if (os.path.exists(TMP_DECOMPILE_FOLDER)):
        shutil.rmtree(TMP_DECOMPILE_FOLDER)
    if (os.path.exists(TMP_DECOMPILE_APKFILE)):
        os.remove(TMP_DECOMPILE_APKFILE)
    if (os.path.exists(DEX_ENCRYPTDATA)):
        os.remove(DEX_ENCRYPTDATA)
    return True

#为生成的apk签名
def signapk_use_testkey(dstapk):
    Log.out("")
    cmdlist = ["python", SIGNAPK_FILE, "-t", dstapk]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

def modifyapk(srcapk, dstapk):
    functions = []
    functions += ["apk_decompile(os.path.abspath(srcapk))"]
    functions += ["modify_xml()"]
    functions += ["apk_compile()"]
    functions += ["generate_dstapk(dstapk)"]
    functions += ["addloader(dstapk)"]
    functions += ["clear_tmp_folder()"]
    functions += ["signapk_use_testkey(dstapk)"]

    result = False
    length = len(functions)
    func_exec_pos = 0
    if (os.path.exists(TRY_CONFIG)):
        f = open(TRY_CONFIG, "r");
        string = f.read()
        f.close()
        saveflag = eval(string)
        filename = saveflag["filename"]
        if (filename != None and filename == os.path.abspath(srcapk)):
            func_exec_pos = saveflag["function_pos"]
        os.remove(TRY_CONFIG)

    for item in range(0, length):
        if (item >= func_exec_pos):
            Log.out("--------------------------------------------")
            result = eval(functions[item])
            if (result == False):
                savestr = '{"function_pos":%d,"filename":r"%s"}' % (item, os.path.abspath(srcapk))
                fd = open(TRY_CONFIG, "w")
                fd.write(savestr)
                fd.close()
                pause()
                return;

def readEncryptArguement():
    s = inputArguement("确认apk是否加壳 : (Y/N) ")
    if (s == None or len(s) <= 0):
        return False
    while s.lower() != "y" and s.lower() != "n":
        s = inputArguement("确认apk是否加壳 : (Y/N) ")
    if (s.lower() == "y"):
        return True
    return False

#解析命令行参数
def parseArguement(argv):
    global APK_SRCFILE
    global APK_NEWPKG
    global APK_NEWLABEL
    global APK_ENCRYPT
    try:
        opts, args = getopt.getopt(argv[1:], "p:l:e")
        if (len(args) == 0):
            return
        for op, value in opts:
            if (op == "-p"):
                APK_NEWPKG = value
            elif (op == "-l"):
                APK_NEWLABEL = value
            elif (op == "-e"):
                APK_ENCRYPT = True

    except getopt.GetoptError as err:
        Log.out(err)
        sys.exit()
    APK_SRCFILE = args[0]

#交互式读取参数
def readArguementFromCmd():
    global APK_SRCFILE
    global APK_NEWPKG
    global APK_NEWLABEL
    global APK_ENCRYPT
    APK_SRCFILE = inputArguement("输入apk文件路径 : ")
    APK_NEWPKG = inputArguement("输入apk新的包名 : ")
    APK_NEWLABEL = inputArguement("输入apk新的名称 : ")
    APK_ENCRYPT = readEncryptArguement()

#检查参数状态
def checkArguement():
    if (APK_SRCFILE == None or len(APK_SRCFILE) <= 0):
        Log.out("[Error...] 缺少apk文件")
        sys.exit(0)
    if (len(APK_SRCFILE) < 4 or APK_SRCFILE[-4:].lower() != ".apk"):
        Log.out("[Error...] %s 不是一个apk文件" % APK_SRCFILE)
        sys.exit(0)
    if (os.path.exists(APK_SRCFILE) == False):
        Log.out("[Error...] 无法定位文件 %s" % APK_SRCFILE)
        sys.exit(0)

    mod_pkgname = APK_NEWPKG != None and len(APK_NEWPKG) > 0
    mod_applabel = APK_NEWLABEL != None and len(APK_NEWLABEL) > 0
    if ((mod_pkgname or mod_applabel or APK_ENCRYPT) == False):
        Log.out("[Error...] APK无任何修改")
        sys.exit(0)
#############################################################################
if (__name__ == "__main__"):
    global MODAPK_DIR
    MODAPK_DIR = os.path.dirname(sys.argv[0])
    if(len(sys.argv) > 1):
        parseArguement(sys.argv)
    else:
        readArguementFromCmd()

checkArguement()

srcapkname = os.path.basename(APK_SRCFILE)
(name, ext) = os.path.splitext(srcapkname)
if (APK_NEWPKG != None and APK_NEWPKG != ""):
    dstapk = name + "-" + APK_NEWPKG + "-mod.apk"
else:
    dstapk = name + "-mod.apk"

#更改当前目录为源文件所在目录
os.chdir(os.path.dirname(os.path.abspath(APK_SRCFILE)))
modifyapk(APK_SRCFILE, dstapk)
