import sys
import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import shutil

TMP_DECOMPILE_FOLDER = "debuild"
APP_ENTRYAPPLICATION = "com.loader.dexloader.WrapperApp"
APP_APPLICATION_KEY = "APPLICATION_CLASS_NAME"
DEX_DECRYPTDATA = "encryptdata.dat"

def log(str, show=True):
    if (show):
        print(str)

def apk_decompile(apkfile):
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, "apktool.jar")
    sys.argv[0] = apktoolfile
    cmdlist = ["java", "-jar", apktoolfile, "d", "-s", "-f" , apkfile, TMP_DECOMPILE_FOLDER]
    log("[Logging...] 正在反编译 %s" % apkfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] %s 反编译出错，请查看日志文件 : decompile_err.txt" % apkfile)
        f = open("decompile_err.txt", "w")
        for line in process.stdout.readlines() :
            tmp = str(line, "utf-8")
            f.write(tmp)
        f.close()
        sys.exit(0);

def apk_compile(apkloaderfile):
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, "apktool.jar")
    sys.argv[0] = apktoolfile
    cmdlist = ["java", "-jar", apktoolfile, "b", TMP_DECOMPILE_FOLDER, apkloaderfile]
    log("[Logging...] 正在回编译 %s" % apkloaderfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] %s 回编译出错，请查看日志文件 : compile_err.txt" % apkloaderfile)
        f = open("compile_err.txt", "w")
        for line in process.stdout.readlines() :
            tmp = str(line, "utf-8")
            f.write(tmp)
        f.close()
        sys.exit(0);

def modify_xml():
    log("[Logging...] 正在编辑AndrodManifest.xml")
    manifest = "%s/AndroidManifest.xml" % TMP_DECOMPILE_FOLDER
    ET.register_namespace('android', "http://schemas.android.com/apk/res/android")
    tree = ET.parse(manifest)
    root = tree.getroot()
    pkgname = root.get("package")
    application = root.find("application");
    appname = application.get("{http://schemas.android.com/apk/res/android}name")
    application.set("{http://schemas.android.com/apk/res/android}name", APP_ENTRYAPPLICATION)
    if (appname != None):
        fullappname = appname
        if (appname.startswith(".")):
            fullappname = pkgname + appname
        ET.SubElement(application, 'meta-data android:name="%s" android:value="%s"' % (APP_APPLICATION_KEY, fullappname))
    tree.write(manifest)
    log("pkgname : %s, appname : %s" % (pkgname, appname))

def generate_decryptdata():
    log("[Logging...] 正在生成%s" % DEX_DECRYPTDATA)
    zf = "%s/assets/%s" %(TMP_DECOMPILE_FOLDER, DEX_DECRYPTDATA)
    log(zf)
    zipf = zipfile.ZipFile(zf, "w")
    zipf.write("%s/classes.dex" % TMP_DECOMPILE_FOLDER, "classes.dex")
    zipf.close()

def copy_loaderclass():
    log("[Logging...] 正在拷贝%s" % "classes.dex")
    sysdir = os.path.dirname(sys.argv[0])
    srcclassdex = os.path.join(sysdir, "classes.dex")
    dstclassdes = "%s/classes.dex" % TMP_DECOMPILE_FOLDER
    shutil.copyfile(srcclassdex, dstclassdes)
    log(srcclassdex)

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
apk_decompile(os.path.abspath(file))
log("")
modify_xml()
log("")
generate_decryptdata()
log("")
copy_loaderclass()
log("")
apk_compile(apkloaderfile)