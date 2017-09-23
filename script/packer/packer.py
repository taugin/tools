#!/usr/bin/python
# coding: UTF-8


import moduleconfig
import Common
import Log
import Utils

import os
import sys
import getopt
import signal

import apkbuilder
import mergeaxml
import sdkconfig
import packconfig
import splitdex

######################################################
PACK_HOME = Common.PACK_HOME
WORKSPACE = os.path.join(PACK_HOME, "workspace")
DSTAPKS = os.path.join(PACK_HOME, "dstapks")
SRCAPKS = os.path.join(PACK_HOME, "srcapks")
SDK_DIR = os.path.join(PACK_HOME, "sdks")
CHANNEL_SDK_DIR = os.path.join(PACK_HOME, "sdks", "channels")
PLUGINS_SDK_DIR = os.path.join(PACK_HOME, "sdks", "plugins")
APK_CFGS = os.path.join(PACK_HOME, "apkcfgs")
######################################################

#检查PIL模块
def check_pil():
    try:
        from PIL import Image
        return True
    except ImportError:
        return False
    else:
        return True

#反编译游戏文件
def decompilegameapk(srcapk, decompiledfolder):
    ret = apkbuilder.apk_decompile(srcapk, decompiledfolder)
    Utils.exitOnFalse(ret)

#拷贝sdk某些文件到反编译文件夹中
def process_sdk(decompiledfolder, sdk_channel):
    config = sdkconfig.SdkConfig(decompiledfolder, sdk_channel)
    config.process()

#处理渠道角标
def process_corner_icon(decompiledfolder, sdk_channel, cornerpos):
    if (check_pil()):
        import icondo
        icondo.process_corner_icon(decompiledfolder, sdk_channel, cornerpos)

#加密关键文件
def encryptKeyFile(decompiledfolder):
    apkbuilder.encryptKeyFile(decompiledfolder)

#回编译游戏
def recompilegameapk(decompiledfolder, recompiledfile):
    ret = apkbuilder.apk_compile(decompiledfolder, recompiledfile)
    Utils.exitOnFalse(ret)

#APK签名
def signapk(unsignapk, signedapk, keystore):
    if (len(keystore) > 0):
        apkbuilder.signapk(unsignapk, signedapk, keystore)
    else:
        Log.out("[Logging...] 无法获取签名");

#apk对齐
def alignapk(unalignapk, finalapk):
    apkbuilder.alignapk(unalignapk, finalapk)

def cleartmp(unsigned_apk, signed_apk):
    try:
        if (os.path.exists(unsigned_apk)):
            os.remove(unsigned_apk)
        if (os.path.exists(signed_apk)):
            os.remove(signed_apk)
    except:
        pass

def modifypkgname(decompiledfolder, pkg_suffix):
    mergeaxml.modify_package(decompiledfolder, pkg_suffix)

def writeProperties(decompiledfolder, properties):
    apkbuilder.writeProperties(decompiledfolder, properties)

def writeManifest(decompiledfolder, manifest):
    mergeaxml.add_meta(decompiledfolder, manifest)

def splitDex(decompiledfolder):
    splitdex.split_dex(decompiledfolder)

def deleteDupSmali(decompiledfolder):
    apkbuilder.clearDupSmali(decompiledfolder)

def packapk(packconfig, channel):
    #获取当前渠道配置的游戏名称
    finalname = packconfig.getfinalname()
    #获取SDK目录
    sdkdirname = channel.getsdkdir();
    #获取所有sdk插件
    pluginlist = channel.getPlugin()
    #获取包名后缀
    suffix = channel.getsuffix()
    #获取签名信息
    keystore = channel.getkeystore()
    #获取母包路径
    srcapkpath = packconfig.getsrcapk()
    #获取SDK名字
    sdkname = channel.getsdkname()
    #获取Properties
    properties = channel.getProperties()
    #获取manifest
    manifest = channel.getManifest()

    #获取角标位置
    cornerpos = channel.getcornerpos()

    #游戏文件路径
    srcapk = os.path.join(PACK_HOME, srcapkpath)

    decompiledfolder = os.path.join(WORKSPACE, finalname + "-" + sdkdirname)
    unsigned_apk = os.path.join(DSTAPKS, finalname + "-" + sdkname + "-unsigned.apk")
    signed_apk = os.path.join(DSTAPKS, finalname + "-" + sdkname + "-signed.apk")
    final_apk = os.path.join(DSTAPKS, finalname + "-" + sdkname + "-final.apk")
    sdk_channel = os.path.join(CHANNEL_SDK_DIR, sdkdirname)

    #反编译APK
    decompilegameapk(srcapk, decompiledfolder)

    #################################################
    #打渠道包
    packchannel(decompiledfolder, sdk_channel, sdkname)
    #打包插件
    packplugins(decompiledfolder, pluginlist)
    #修改AndroidManifest.xml里面的包名
    modifypkgname(decompiledfolder, suffix)

    #修改developer_config.properties
    writeProperties(decompiledfolder, properties)
    #添加manifest
    writeManifest(decompiledfolder, manifest)
    #################################################
    #分割DEX
    #splitDex(decompiledfolder)

    #删除重复的smali文件
    deleteDupSmali(decompiledfolder)

    #处理渠道角标
    process_corner_icon(decompiledfolder, sdk_channel, cornerpos)

    #加密关键文件
    encryptKeyFile(decompiledfolder)

    #调用渠道自定义脚本
    pyPath = os.path.normpath(os.path.join(sdk_channel, "channel_spec.py"))
    apkbuilder.callChannelSpec(pyPath, channel.getSpecParams())

    recompilegameapk(decompiledfolder, unsigned_apk)
    signapk(unsigned_apk, signed_apk, keystore)
    alignapk(signed_apk, final_apk)
    cleartmp(unsigned_apk, signed_apk)

#打包渠道sdk
def packchannel(decompiledfolder, sdk_channel, sdkname):
    Log.out("[Logging...] +++++++++++++++++++++++++++++++++++++++");
    Log.out("[Logging...] 打包配置渠道 : [%s]" % sdkname);
    process_sdk(decompiledfolder, sdk_channel)
    Log.out("[Logging...] =======================================\n");

#打包插件sdk
def packplugins(decompiledfolder, pluginlist):
    Log.out("[Logging...] +++++++++++++++++++++++++++++++++++++++");
    sdk_channel = None
    if (pluginlist != None):
        for plugin in pluginlist:
            pname = Utils.getvalue(plugin, "name")
            if (Utils.isEmpty(pname)) :
                continue
            sdk_channel = os.path.join(PLUGINS_SDK_DIR, pname)
            if (os.path.exists(sdk_channel)):
                Log.out("[Logging...] 打包配置插件 : [%s]" % pname);
                process_sdk(decompiledfolder, sdk_channel)
    Log.out("[Logging...] =======================================\n");

def pack(appName, channelNo):
    channelFile = os.path.join(APK_CFGS, appName, "channels.xml")
    channelFile = os.path.normpath(channelFile)
    if (not os.path.exists(channelFile)):
        Log.out("[Logging...] 缺少配置文件 : [%s]" % channelFile)
        return
    packConfig = packconfig.PackConfig(channelFile);
    packConfig.parse()
    channelList = packConfig.getChannelList();
    if (channelList == None or len(channelList) <= channelNo):
        Log.out("[Logging...] 渠道序号错误 : [%d]" % channelNo)
        return
    channel = channelList[channelNo]

    Log.out("[Logging...] 应用打包信息 : [%s, %s]\n" % (appName, channel.getsdkname()))
    packapk(packConfig, channel)

def pack_apk_from_args(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "a:c:h")
        for op, value in opts:
            if (op == "-a"):
                appName = value
            elif (op == "-c") :
                channelNo = value
            elif (op == "-h") :
                Log.out("[Logging...] 缺少参数 : %s -a appName -c channelNo" % os.path.basename(sys.argv[0]), True);
                sys.exit()
    except getopt.GetoptError as err:
        Log.out(err)
        sys.exit()

    if appName != None and channelNo != None and channelNo.isdigit():
        pack(appName, int(channelNo))

def inputInRange(prompt, maxValue):
    try:
        value = input(prompt)
        while value == None or not value.isdigit() or int(value) >= maxValue:
            value = input(prompt)
        return int(value)
    except KeyboardInterrupt:
        sys.exit(0)

def printAppList(apkcfg):
    print("打包应用列表:")
    for index in range(len(apkcfg)):
        print("[%s] : %s" % (index, apkcfg[index]))

def printChannelList(chlist):
    print("打包渠道列表:")
    for index in range(len(chlist)):
        print("[%s] : %s" % (index, chlist[index].getsdkname()))

def pack_apk_from_select():
    apkcfg = os.listdir(APK_CFGS)
    if apkcfg == None or len(apkcfg) <= 0:
        Log.out("[Logging...] 缺少打包应用")
        sys.exit(0)
    printAppList(apkcfg)
    index = inputInRange("选择应用编号 : ", len(apkcfg))
    if index >= len(apkcfg):
        Log.out("[Logging...] 选择参数错误 : [%s]" % index)
        sys.exit(0)
    appName = apkcfg[index]
    channelFile = os.path.join(APK_CFGS, appName, "channels.xml")
    channelFile = os.path.normpath(channelFile)
    if not os.path.exists(channelFile):
        Log.out("[Logging...] 确实配置文件 : [%s]" % channelFile)
        sys.exit(0)

    packConfig = packconfig.PackConfig(channelFile)
    packConfig.parse()
    channelList = packConfig.getChannelList()
    if channelList == None or len(channelList) <= 0:
        Log.out("[Logging...] 缺少打包渠道")
        sys.exit(0)

    printChannelList(channelList)
    index = inputInRange("选择渠道编号 : ", len(channelList))
    if index > len(channelList):
        Log.out("[Logging...] 渠道参数错误 : [%s]" % index)
        sys.exit(0)
    channel = channelList[index]

    print("\n")
    Log.out("[Logging...] 应用打包信息 : [%s, %s]\n" % (appName, channel.getsdkname()))
    packapk(packConfig, channel)

def signalHandler(signum, frame):
    Log.out("\n[Logging...] 用户主动退出")

def registerSignal():
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

if __name__ == "__main__":
    registerSignal()
    appName = None
    channelNo = None
    if (len(sys.argv) == 1):
        pack_apk_from_select()
    else:
        pack_apk_from_args(sys.argv)