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

import platform
import subprocess
import shutil
import getopt

import apkbuilder
import merge_xml
import sdkconfig
import packconfig

#反编译游戏文件
def decompilegameapk(gameapk, decompiledfolder):
    return apkbuilder.apk_decompile(gameapk, decompiledfolder)

#合并AndroidManifest.xml文件
def merge_androidmanifest(decompiledfolder, sdkfolder):
    return merge_xml.merge_androidmanifest(decompiledfolder, sdkfolder)

#拷贝sdk某些文件到反编译文件夹中
def copy_sdk_files(decompiledfolder, sdkfolder):
    configFile = os.path.join(sdkfolder, "sdk_config.xml")
    config = sdkconfig.SdkConfig(configFile)
    return config.process_config(decompiledfolder, sdkfolder) and config.process_plugin(decompiledfolder, sdkfolder)

#渠道DEX转smali
def dex2smali(decompiledfolder, sdkfolder):
    dexfile = os.path.join(sdkfolder, "classes.dex")
    outdir = os.path.join(decompiledfolder, "smali");
    apkbuilder.baksmali(dexfile, outdir)

#回编译游戏
def recompilegameapk(decompiledfolder, recompiledfile):
    return apkbuilder.apk_compile(decompiledfolder, recompiledfile)

#APK签名
def signapk(unsignapk, signedapk, keystore):
    apkbuilder.signapk(unsignapk, signedapk, keystore)

#apk对齐
def alignapk(unalignapk, finalapk):
    apkbuilder.alignapk(unalignapk, finalapk)

def clear_tmp(unsigned_apk, signed_apk):
    try:
        if (os.path.exists(unsigned_apk)):
            os.remove(unsigned_apk)
        if (os.path.exists(signed_apk)):
            os.remove(signed_apk)
    except:
        pass

def modifymanifest(decompiledfolder, pkg_suffix):
    merge_xml.modify_package(decompiledfolder, pkg_suffix)

def getvalue(item, key):
    try:
        return item[key]
    except:
        return None

def packapk(channel):
    gamename = channel.getgamename()
    sdkdir = channel.getsdkdir();
    pluginlist = channel.getPlugin()
    suffix = channel.getsdksuffix()
    gameapk = os.path.join(Common.GAMES, gamename, gamename + ".apk")
    Log.out(gameapk)

    decompiledfolder = os.path.join(Common.WORKSPACE, sdkdir)
    unsigned_apk = os.path.join(Common.PACKAGES, sdkdir + "-unsigned.apk")
    signed_apk = os.path.join(Common.PACKAGES, sdkdir + "-signed.apk")
    final_apk = os.path.join(Common.PACKAGES, sdkdir + "-final.apk")
    sdk_channel = os.path.join(Common.SDK, sdkdir)

    #反编译APK
    decompilegameapk(gameapk, decompiledfolder)

    #################################################
    #打渠道包
    packchannel(decompiledfolder, sdk_channel)
    #打包插件
    packplugins(decompiledfolder, pluginlist)
    #修改AndroidManifest.xml里面的包名
    modifymanifest(decompiledfolder, suffix)
    #################################################

    recompilegameapk(decompiledfolder, unsigned_apk)
    signapk(unsigned_apk, signed_apk, None)
    alignapk(signed_apk, final_apk)
    clear_tmp(unsigned_apk, signed_apk)

#打包渠道sdk
def packchannel(decompiledfolder, sdkfolder):
    Log.out("[Logging...] 打包渠道SDK ##############################");
    merge_androidmanifest(decompiledfolder, sdkfolder)
    copy_sdk_files(decompiledfolder, sdkfolder)
    dex2smali(decompiledfolder, sdkfolder)

#打包插件sdk
def packplugins(decompiledfolder, pluginlist):
    Log.out("[Logging...] 打包插件SDK ##############################");
    sdkfolder = None
    if (pluginlist != None):
        for plugin in pluginlist:
            pname = getvalue(plugin, "name")
            if (pname == None) :
                continue
            sdkfolder = os.path.join(Common.SDK, pname)
            if (os.path.exists(sdkfolder)):
                merge_androidmanifest(decompiledfolder, sdkfolder)
                copy_sdk_files(decompiledfolder, sdkfolder)
                dex2smali(decompiledfolder, sdkfolder)

def pack():
    packConfig = packconfig.PackConfig("E:\\Github\\tools\\games\\AbchDemo\\config\\channels.xml");
    packConfig.parse()
    packapk(packConfig.getChannelList()[0])

pack()