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
import process_config

#反编译游戏文件
def decompilegameapk(gameapk, decompiledfolder):
    return apkbuilder.apk_decompile(gameapk, decompiledfolder)

#合并AndroidManifest.xml文件
def merge_androidmanifest(decompiledfolder, sdkfolder):
    return merge_xml.merge_androidmanifest(decompiledfolder, sdkfolder)

#拷贝sdk某些文件到反编译文件夹中
def copy_sdk_files(decompiledfolder, sdkfolder):
    return process_config.process_config(decompiledfolder, sdkfolder)

#渠道DEX转smali
def dex2smali(decompiledfolder, sdkfolder):
    dexfile = os.path.join(sdkfolder, "classes.dex")
    outdir = os.path.join(decompiledfolder, "smali");
    apkbuilder.baksmali(dexfile, outdir)

#apk对齐
def aliginApk(finalapk):
    pass

#回编译游戏
def recompilegameapk(decompiledfolder, recompiledfile):
    return apkbuilder.apk_compile(decompiledfolder, recompiledfile)

def pack(gameapk, channel):
    decompiledfolder = os.path.join(Common.WORKSPACE, channel)
    outapk = os.path.join(Common.PACKAGES, channel + ".apk")
    sdkfolder = os.path.join(Common.SDK, channel)
    decompilegameapk(gameapk, decompiledfolder)
    merge_androidmanifest(decompiledfolder, sdkfolder)
    copy_sdk_files(decompiledfolder, sdkfolder)
    dex2smali(decompiledfolder, sdkfolder)
    recompilegameapk(decompiledfolder, outapk)
    
pack("D:\\Github\\tools\\games\\AbchDemo.apk", "ucsdk")