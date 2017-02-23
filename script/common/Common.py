import os
import platform

##############################通用函数###########################
__all__ = []

#主目录
#获取Common.py文件所在的目录
_DIR = os.path.dirname(__file__)
_HOME_DIR = os.path.join(_DIR, "..", "..")
#规范化路径显示，如A/foo/../B 变成 A/B
HOME_DIR = os.path.normpath(_HOME_DIR)

#执行文件存放目录
BIN_DIR = os.path.join(HOME_DIR, "bin")

#脚本文件存放目录
SCRIPT_DIR = os.path.join(HOME_DIR, "script")

#库文件存放目录
LIB_DIR = os.path.join(HOME_DIR, "libs")

#签名文件存放目录
KEYSTORES_DIR = os.path.join(HOME_DIR, "sdks/keystore")

#可执行文件后缀
BIN_SUFFIX = ""
if (platform.system().lower() == "windows"):
    BIN_SUFFIX = ".exe"
else:
    BIN_SUFFIX = ""

#路径分隔符    
SEPERATER = os.path.sep

#########################jar包文件路径定义#################################
#APKTOOL的jar包，版本是2.1.1
APKTOOL_JAR = os.path.join(LIB_DIR, "apktool_2.1.1.jar")

#签名jar
SIGNAPK_JAR = os.path.join(LIB_DIR, "signapk.jar")

#AXMLPrinter2的jar包
AXMLPRINTER_JAR = os.path.join(LIB_DIR, "AXMLPrinter2.jar")

#壳DEX文件
SHELL_DEX = os.path.join(LIB_DIR, "classes.dex");

#smali-2.1.3
SMALI_JAR = os.path.join(LIB_DIR, "smali-2.1.3.jar");

#baksmali-2.1.3
BAKSMALI_JAR = os.path.join(LIB_DIR, "baksmali-2.1.3.jar");


#########################可执行文件文件路径定义#################################

#AAPT可执行文件
AAPT_BIN = os.path.join(BIN_DIR, "aapt%s" % BIN_SUFFIX)

#keytool可执行文件
KEYTOOL = "keytool"

#jarsigner可执行文件
JARSIGNER="jarsigner"

#adb
ADB = os.path.join(BIN_DIR, "adb%s" % BIN_SUFFIX);

#java
JAVA = "java"

#apk对齐工具
ZIPALIGN = os.path.join(BIN_DIR, "zipalign%s" % BIN_SUFFIX)

#########################apk签名参数#################################
#jarsigner 在JDK7上需要的参数
JDK7ARG="-tsa https://timestamp.geotrust.com/tsa -digestalg SHA1 -sigalg MD5withRSA"
X509 = os.path.join(KEYSTORES_DIR, "testkey.x509.pem")
PK8 = os.path.join(KEYSTORES_DIR, "testkey.pk8")

#########################Androidmanifest.xml参数#################################
#自定义替换字符串
RE_STRING = "PACKAGE_NAME_ABC"

#Androidmanifest名称空间
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

#支付服务名称
PAY_SERVICE = "com.cocospay.CocosPayService"

#支付框架入口Activity
PAY_ACTIVITY = "com.coco.iap.PayActivity"

#跳转的目标Activity的meta-data的key值
PAYACTIVITY_ENTRY_NAME = "dest_activity"

#联通入口Activity
UNICOM_ACTIVITY = "com.unicom.dcLoader.welcomeview"
#跳转的目标Activity的meta-data的key值
UNICOMPAYACTIVITY_ENTRY_NAME = "UNICOM_DIST_ACTIVITY"

#入口Activity的IntentFilter
MAIN_ACTIVITY_XPATH = ".//action/[@{%s}name='android.intent.action.MAIN']/../category/[@{%s}name='android.intent.category.LAUNCHER']/../.." % (XML_NAMESPACE, XML_NAMESPACE)
CATEGORY_XPATH = ".//action/[@{%s}name='android.intent.action.MAIN']/../category/[@{%s}name='android.intent.category.LAUNCHER']/.." % (XML_NAMESPACE, XML_NAMESPACE)

#plugins文件
PLUGIN_FILE = "assets/plugins.xml"
#itemmapper文件
ITEM_MAPPER = "assets/ItemMapper.xml"
#itemmapper文件
PAY_STUBDATA = "assets/com.coco.iap.stub.dat"
#ccp_strings文件
COMPANYFILE = "assets/ccp_strings.xml"


################################################################################
#pack
WORKSPACE = os.path.join(HOME_DIR, "workspace")

PACKAGES = os.path.join(HOME_DIR, "packages")

GAMES = os.path.join(HOME_DIR, "games")

SDK_DIR = os.path.join(HOME_DIR, "sdks")

CHANNEL_SDK_DIR = os.path.join(HOME_DIR, "sdks", "channels")

PLUGINS_SDK_DIR = os.path.join(HOME_DIR, "sdks", "plugins")

###########################################################################
def pause():
    input("按回车键退出...")