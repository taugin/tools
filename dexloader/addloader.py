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
DEX_DECRYPTDATA = "encryptdata.dat"
DEX_DECRYPTDATA_PATH = os.path.join(TMP_DECOMPILE_FOLDER, "assets", DEX_DECRYPTDATA)
APP_MODIFIED_MANIFEST = os.path.join(TMP_DECOMPILE_FOLDER, MANIFEST_FILE)
SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "signtool", "signapk.py")
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

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

def apk_compile():
    thisdir = os.path.dirname(sys.argv[0])
    apktoolfile = os.path.join(thisdir, "apktool.jar")
    sys.argv[0] = apktoolfile
    cmdlist = ["java", "-jar", apktoolfile, "b", TMP_DECOMPILE_FOLDER, TMP_DECOMPILE_APKFILE]
    log("[Logging...] 正在回编译 %s" % apkloaderfile)
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        log("[Error...] %s 回编译出错，请查看日志文件 : compile_err.txt" % TMP_DECOMPILE_APKFILE)
        f = open("compile_err.txt", "w")
        for line in process.stdout.readlines() :
            tmp = str(line, "utf-8")
            f.write(tmp)
        f.close()
        sys.exit(0);

def modify_xml():
    log("[Logging...] 正在编辑AndrodManifest.xml")
    manifest = "%s/AndroidManifest.xml" % TMP_DECOMPILE_FOLDER
    ET.register_namespace('android', XML_NAMESPACE)
    tree = ET.parse(manifest)
    root = tree.getroot()
    pkgname = root.get("package")
    application = root.find("application");
    appname = application.get("{%s}name" % XML_NAMESPACE)
    application.set("{%s}name" % XML_NAMESPACE, APP_ENTRYAPPLICATION)
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

def generate_loaderapk(apkloaderfile):
    log("[Logging...] 正在生成%s" % apkloaderfile)
    shutil.copyfile(basename, apkloaderfile)

def zip_loaderanddat(apkloaderfile):
    log("[Logging...] 正在拷贝%s" % "classes.dex")
    subprocess.call([AAPT_FILE, "rv", apkloaderfile, MANIFEST_FILE])
    subprocess.call([AAPT_FILE, "rv", apkloaderfile, "classes.dex"])
    subprocess.call([AAPT_FILE, "rv", apkloaderfile, "assets/%s" % DEX_DECRYPTDATA])
    sysdir = os.path.dirname(sys.argv[0])
    szf = zipfile.ZipFile(TMP_DECOMPILE_APKFILE, "r")
    srcclassdex = os.path.join(sysdir, "classes.dex")
    zf = zipfile.ZipFile(apkloaderfile, "a")
    zf.write(srcclassdex, "classes.dex")
    zf.write(DEX_DECRYPTDATA_PATH, "assets/%s" % DEX_DECRYPTDATA)
    manifest = open(MANIFEST_FILE, "wb")
    manifest.write(szf.read(MANIFEST_FILE))
    manifest.close()
    zf.write(MANIFEST_FILE)
    zf.close()
    szf.close()

def clear_tmp_folder():
    log("[Logging...] 清除临时文件")
    shutil.rmtree(TMP_DECOMPILE_FOLDER)
    os.remove(TMP_DECOMPILE_APKFILE)
    os.remove(MANIFEST_FILE)

def signapk_use_testkey(apkloaderfile):
    cmdlist = ["python", SIGNAPK_FILE, "-t", apkloaderfile]
    subprocess.call(cmdlist)

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

apk_decompile(os.path.abspath(file))
log("")
modify_xml()
log("")
generate_decryptdata()
log("")
apk_compile()
log("")
generate_loaderapk(apkloaderfile)
log("")
zip_loaderanddat(apkloaderfile)
log("")
clear_tmp_folder()
log("")
signapk_use_testkey(apkloaderfile)
