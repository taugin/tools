#!/usr/bin/python
# coding: UTF-8
import sys
import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import shutil
import platform

MANIFEST_FILE = "AndroidManifest.xml"
TMP_DECOMPILE_FOLDER = "debuild"
TMP_DECOMPILE_APKFILE = "debuild.apk"
APP_ENTRYAPPLICATION = "com.loader.dexloader.WrapperApp"
APP_APPLICATION_KEY = "APPLICATION_CLASS_NAME"
DEX_ENCRYPTDATA = "encryptdata.dat"
DEX_DECRYPTDATA_PATH = os.path.join(TMP_DECOMPILE_FOLDER, "assets", DEX_ENCRYPTDATA)
APP_MODIFIED_MANIFEST = os.path.join(TMP_DECOMPILE_FOLDER, MANIFEST_FILE)
SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "signtool", "signapk.py")
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"
TRY_CONFIG = "addloader.tryagain"


EXE = ""
if (platform.system().lower() == "windows"):
    EXE = ".exe"
AAPT = "aapt%s" % EXE
AAPT_FILE = os.path.join(os.path.dirname(sys.argv[0]), AAPT)

def log(str, show=True):
    if (show):
        print(str)

def apk_decompile(apkfile):
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, "apktool_2.0.0.jar")
    cmdlist = ["java", "-jar", apktoolfile, "d", "-s", "-f" , apkfile, "-o", TMP_DECOMPILE_FOLDER]
    log("[Logging...] 正在反编译 %s" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] %s 反编译出错 ...")
        return False
    else:
        return True

def apk_compile():
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, "apktool_2.0.0.jar")
    cmdlist = ["java", "-jar", apktoolfile, "b", TMP_DECOMPILE_FOLDER, "-o", TMP_DECOMPILE_APKFILE]
    log("[Logging...] 正在回编译 %s" % TMP_DECOMPILE_APKFILE)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] %s 回编译出错 ...")
        return False
    else:
        return True

def modify_xml():
    log("[Logging...] 正在编辑 AndrodManifest.xml")
    manifest = "%s/AndroidManifest.xml" % TMP_DECOMPILE_FOLDER
    ET.register_namespace('android', XML_NAMESPACE)
    tree = ET.parse(manifest)
    root = tree.getroot()
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
    tree.write(manifest)
    return True


def generate_encryptdata():
    zf = "%s/assets/%s" %(TMP_DECOMPILE_FOLDER, DEX_ENCRYPTDATA)
    log("[Logging...] 正在生成 %s" % zf)
    assetsdir = "%s/assets/" % TMP_DECOMPILE_FOLDER
    if (os.path.exists(assetsdir) == False):
        os.mkdir(assetsdir)
    zipf = zipfile.ZipFile(zf, "w")
    zipf.write("%s/classes.dex" % TMP_DECOMPILE_FOLDER, "classes.dex")
    zipf.close()
    return True

def generate_loaderapk(apkloaderfile):
    log("[Logging...] 正在生成 %s" % apkloaderfile)
    shutil.copyfile(basename, apkloaderfile)
    return True

def zip_loaderanddat(apkloaderfile):
    log("[Logging...] 正在拷贝 assets/%s" % DEX_ENCRYPTDATA)
    log("[Logging...] 正在拷贝 %s" % MANIFEST_FILE)
    log("[Logging...] 正在拷贝 %s" % "classes.dex")
    subprocess.call([AAPT_FILE, "rv", apkloaderfile, MANIFEST_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([AAPT_FILE, "rv", apkloaderfile, "classes.dex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call([AAPT_FILE, "rv", apkloaderfile, "assets/%s" % DEX_ENCRYPTDATA], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sysdir = os.path.dirname(sys.argv[0])
    szf = zipfile.ZipFile(TMP_DECOMPILE_APKFILE, "r")
    srcclassdex = os.path.join(sysdir, "classes.dex")
    zf = zipfile.ZipFile(apkloaderfile, "a")
    zf.write(srcclassdex, "classes.dex")
    zf.write(DEX_DECRYPTDATA_PATH, "assets/%s" % DEX_ENCRYPTDATA)
    manifest = open(MANIFEST_FILE, "wb")
    manifest.write(szf.read(MANIFEST_FILE))
    manifest.close()
    zf.write(MANIFEST_FILE)
    zf.close()
    szf.close()
    return True

def clear_tmp_folder():
    log("[Logging...] 清除临时文件")
    shutil.rmtree(TMP_DECOMPILE_FOLDER)
    os.remove(TMP_DECOMPILE_APKFILE)
    os.remove(MANIFEST_FILE)
    return True

def signapk_use_testkey(apkloaderfile):
    log("")
    cmdlist = ["python", SIGNAPK_FILE, "-t", apkloaderfile]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

def process_addloader(file, apkloaderfile):
    functions = []
    functions += ["apk_decompile(os.path.abspath(file))"]
    functions += ["modify_xml()"]
    functions += ["generate_encryptdata()"]
    functions += ["apk_compile()"]
    functions += ["generate_loaderapk(apkloaderfile)"]
    functions += ["zip_loaderanddat(apkloaderfile)"]
    functions += ["clear_tmp_folder()"]
    functions += ["signapk_use_testkey(apkloaderfile)"]

    result = False
    length = len(functions)
    func_exec_pos = 0
    if (os.path.exists(TRY_CONFIG)):
        f = open(TRY_CONFIG, "r");
        string = f.read()
        f.close()
        saveflag = eval(string)
        func_exec_pos = saveflag["function_pos"]

    for item in range(0, length):
        if (item >= func_exec_pos):
            log("--------------------------------------------")
            result = eval(functions[item])
            if (result == False):
                savestr = '{"function_pos":%d}' % item
                fd = open(TRY_CONFIG, "w")
                fd.write(savestr)
                fd.close()
                return;
    if (os.path.exists(TRY_CONFIG)):
        os.remove(TRY_CONFIG)



if (len(sys.argv) < 2):
    log("[Logging...] 缺少参数: %s <*.apk>" % os.path.basename(sys.argv[0]), True);
    sys.exit()
file = sys.argv[1]
if (len(file) < 4 or file[-4:].lower() != ".apk"):
    log("[Error...] %s 不是一个apk文件" % file)
    sys.exit(0)

if (os.path.exists(file) == False):
    log("[Error...] 无法定位文件 %s" % file)
    sys.exit(0)
basename = os.path.basename(file)
(name, ext) = os.path.splitext(basename)
apkloaderfile = name + "-loader.apk"

#更改当前目录为源文件所在目录
os.chdir(os.path.dirname(os.path.abspath(file)))
process_addloader(file, apkloaderfile)
