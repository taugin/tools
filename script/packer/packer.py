#!/usr/bin/python
# coding: UTF-8


import moduleconfig
import Common
import Log
import Utils

import os

import apkbuilder
import mergeaxml
import sdkconfig
import packconfig
import splitdex

#反编译游戏文件
def decompilegameapk(gameapk, decompiledfolder):
    ret = apkbuilder.apk_decompile(gameapk, decompiledfolder)
    Utils.exitOnFalse(ret)

#拷贝sdk某些文件到反编译文件夹中
def process_sdk(decompiledfolder, sdkfolder):
    config = sdkconfig.SdkConfig(decompiledfolder, sdkfolder)
    config.process()

#回编译游戏
def recompilegameapk(decompiledfolder, recompiledfile):
    ret = apkbuilder.apk_compile(decompiledfolder, recompiledfile)
    Utils.exitOnFalse(ret)

#APK签名
def signapk(unsignapk, signedapk, keystore):
    apkbuilder.signapk(unsignapk, signedapk, keystore)

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

def packapk(packconfig, channel):
    #获取当前渠道配置的游戏名称
    gamename = channel.getgamename()
    #获取SDK目录
    sdkdirname = channel.getsdkdir();
    #获取所有sdk插件
    pluginlist = channel.getPlugin()
    #获取包名后缀
    suffix = channel.getsdksuffix()
    #获取签名信息
    keystore = channel.getkeystore()
    #获取母包路径
    gameapkpath = packconfig.getgameapk()
    #获取SDK名字
    sdkname = channel.getsdkname()
    #获取Properties
    properties = channel.getProperties()
    #获取manifest
    manifest = channel.getManifest()

    #游戏文件路径
    gameapk = os.path.join(Common.PACK_HOME, gameapkpath)

    decompiledfolder = os.path.join(Common.WORKSPACE, gamename + "-" + sdkdirname)
    unsigned_apk = os.path.join(Common.DSTAPKS, gamename + "-" + sdkname + "-unsigned.apk")
    signed_apk = os.path.join(Common.DSTAPKS, gamename + "-" + sdkname + "-signed.apk")
    final_apk = os.path.join(Common.DSTAPKS, gamename + "-" + sdkname + "-final.apk")
    sdk_channel = os.path.join(Common.CHANNEL_SDK_DIR, sdkdirname)

    #反编译APK
    decompilegameapk(gameapk, decompiledfolder)

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
    splitDex(decompiledfolder)

    recompilegameapk(decompiledfolder, unsigned_apk)
    signapk(unsigned_apk, signed_apk, keystore)
    alignapk(signed_apk, final_apk)
    cleartmp(unsigned_apk, signed_apk)

#打包渠道sdk
def packchannel(decompiledfolder, sdkfolder, sdkname):
    Log.out("[Logging...] +++++++++++++++++++++++++++++++++++++++");
    Log.out("[Logging...] 打包配置渠道 : [%s]" % sdkname);
    process_sdk(decompiledfolder, sdkfolder)
    Log.out("[Logging...] =======================================\n");

#打包插件sdk
def packplugins(decompiledfolder, pluginlist):
    Log.out("[Logging...] +++++++++++++++++++++++++++++++++++++++");
    sdkfolder = None
    if (pluginlist != None):
        for plugin in pluginlist:
            pname = Utils.getvalue(plugin, "name")
            if (Utils.isEmpty(pname)) :
                continue
            sdkfolder = os.path.join(Common.PLUGINS_SDK_DIR, pname)
            if (os.path.exists(sdkfolder)):
                Log.out("[Logging...] 打包配置插件 : [%s]" % pname);
                process_sdk(decompiledfolder, sdkfolder)
    Log.out("[Logging...] =======================================\n");

def pack():
    channelFile = os.path.join(Common.PACK_HOME, "apkconfigs/AbchDemo/channels.xml")
    channelFile = os.path.normpath(channelFile)
    packConfig = packconfig.PackConfig(channelFile);
    packConfig.parse()
    channel = packConfig.getChannelList()[0]
    packapk(packConfig, channel)

pack()