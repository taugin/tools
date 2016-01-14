#!/usr/bin/python
# coding: UTF-8
import sys
import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import shutil
import platform
import getopt

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
APKTOOL_JAR = "apktool_2.0.3.jar"
TRY_CONFIG = "modapk.tryagain"

NEW_PKGNAME = ""
APP_LABEL = ""
ENCRY_APK = False


EXE = ""
if (platform.system().lower() == "windows"):
    EXE = ".exe"
AAPT = "aapt%s" % EXE
AAPT_FILE = os.path.join(os.path.dirname(sys.argv[0]), AAPT)

def log(str, show=True):
    if (show):
        print(str)

def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        log("操作完成，按任意键退出", True)
        msvcrt.getch()

def apk_decompile(apkfile):
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, APKTOOL_JAR)
    cmdlist = ["java", "-jar", apktoolfile, "d", "-s", "-f" , apkfile, "-o", TMP_DECOMPILE_FOLDER]
    log("[Logging...] 反编译中 %s" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] 反编译出错 ...")
        return False
    else:
        return True

def apk_compile():
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, APKTOOL_JAR)
    cmdlist = ["java", "-jar", apktoolfile, "b", TMP_DECOMPILE_FOLDER, "-o", TMP_DECOMPILE_APKFILE]
    log("[Logging...] 回编译中 %s" % TMP_DECOMPILE_APKFILE)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] 回编译出错 ...")
        return False
    else:
        return True

#修改应用程序包名
def modify_packagename_ifneed(root):
    if (NEW_PKGNAME != None and NEW_PKGNAME != ""):
        log("[Logging...] 修改包名 " + NEW_PKGNAME)
        root.set("package", NEW_PKGNAME)

#修改应用程序名称
def modify_applabel_ifneed(root):
    if (APP_LABEL != None and APP_LABEL != ""):
        log("[Logging...] 修改应用名称 " + APP_LABEL)
        application = root.find("application");
        application.set("{%s}label" % XML_NAMESPACE, APP_LABEL)

#增加关于loader的一些信息
def modify_appname_forloader(root):
    # 不加密Apk时直接返回
    if (ENCRY_APK == False):
        return

    pkgname = root.get("package")
    application = root.find("application");
    appname = application.get("{%s}name" % XML_NAMESPACE)
    if (appname != None and appname == APP_ENTRYAPPLICATION):
        log("[Logging...] 貌似已经加过密了，查看一下吧")
        return False
    log("[Logging...] 设置入口 Application : %s" % APP_ENTRYAPPLICATION)
    application.set("{%s}name" % XML_NAMESPACE, APP_ENTRYAPPLICATION)
    log("[Logging...] 应用包名 %s" % pkgname)
    if (appname != None):
        fullappname = appname
        if (appname.startswith(".")):
            fullappname = pkgname + appname
        log("[Logging...] 设置真正 Application : %s" % fullappname)
        ET.SubElement(application, 'meta-data android:name="%s" android:value="%s"' % (APP_APPLICATION_KEY, fullappname))

#修改AndroidManifest.xml
def modify_xml():
    log("[Logging...] 正在编辑 AndrodManifest.xml")
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
    log("[Logging...] 正在生成 %s" % dstapk)
    shutil.copyfile(srcapkname, dstapk)

#将classes.des压缩为encryptdata.dat
def generate_encryptdata():
    basezf = zipfile.ZipFile(srcapkname, "r")
    zipf = zipfile.ZipFile(DEX_ENCRYPTDATA,"w")
    zipf.writestr("classes.dex", basezf.read("classes.dex"))
    zipf.close()
    basezf.close()
    return DEX_ENCRYPTDATA

def addloader(dstapk):
    # 不加密Apk时直接返回
    if (ENCRY_APK == False):
        return True

    subprocess.call([AAPT_FILE, "r", dstapk, MANIFEST_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([AAPT_FILE, "r", dstapk, "classes.dex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([AAPT_FILE, "r", dstapk, "assets/%s" % DEX_ENCRYPTDATA], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    szf = zipfile.ZipFile(TMP_DECOMPILE_APKFILE, "r")
    

    zf = zipfile.ZipFile(dstapk, "a")

    #将原classes.dex文件压缩改名后写入assets文件夹
    log("[Logging...] 正在拷贝 assets/%s" % DEX_ENCRYPTDATA)
    encryptdata_file = generate_encryptdata();
    zf.write(encryptdata_file, "assets/%s" % DEX_ENCRYPTDATA, zipfile.ZIP_DEFLATED)

    #将壳classes.dex文件写入
    log("[Logging...] 正在拷贝 %s" % "classes.dex")
    srcclassdex = os.path.join(sysdir, "classes.dex")
    zf.write(srcclassdex, "classes.dex")

    #将修改后的AndroidManifest.xml写入
    log("[Logging...] 正在拷贝 %s" % MANIFEST_FILE)
    zf.writestr(MANIFEST_FILE, szf.read(MANIFEST_FILE))

    zf.close()
    szf.close()
    return True

#清除临时文件夹
def clear_tmp_folder():
    log("[Logging...] 清除临时文件")
    if (os.path.exists(TMP_DECOMPILE_FOLDER)):
        shutil.rmtree(TMP_DECOMPILE_FOLDER)
    if (os.path.exists(TMP_DECOMPILE_APKFILE)):
        os.remove(TMP_DECOMPILE_APKFILE)
    if (os.path.exists(DEX_ENCRYPTDATA)):
        os.remove(DEX_ENCRYPTDATA)
    return True

#为生成的apk签名
def signapk_use_testkey(dstapk):
    log("")
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
            log("--------------------------------------------")
            result = eval(functions[item])
            if (result == False):
                savestr = '{"function_pos":%d,"filename":r"%s"}' % (item, os.path.abspath(srcapk))
                fd = open(TRY_CONFIG, "w")
                fd.write(savestr)
                fd.close()
                pause()
                return;


USAGE = "[Logging...] 缺少参数: %s [-e] [-p newpkgname] [-l labelname] <*.apk>" % os.path.basename(sys.argv[0])
#############################################################################
if (__name__ == "__main__"):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:l:e")
        if (len(opts) == 0):
            log(USAGE, True);
            sys.exit()
        for op, value in opts:
            if (op == "-p"):
                NEW_PKGNAME = value
            elif (op == "-l"):
                APP_LABEL = value
            elif (op == "-e"):
                ENCRY_APK = True

    except getopt.GetoptError as err:
        log(err)
        sys.exit()
if (len(args) < 1):
    log(USAGE, True);
    sys.exit()

sysdir = os.path.dirname(sys.argv[0])
file = args[0]
if (len(file) < 4 or file[-4:].lower() != ".apk"):
    log("[Error...] %s 不是一个apk文件" % file)
    sys.exit(0)

if (os.path.exists(file) == False):
    log("[Error...] 无法定位文件 %s" % file)
    sys.exit(0)
srcapkname = os.path.basename(file)
(name, ext) = os.path.splitext(srcapkname)
if (NEW_PKGNAME != None and NEW_PKGNAME != ""):
    dstapk = name + "-" + NEW_PKGNAME + "-mod.apk"
else:
    dstapk = name + "-mod.apk"

#更改当前目录为源文件所在目录
os.chdir(os.path.dirname(os.path.abspath(file)))
modifyapk(file, dstapk)
