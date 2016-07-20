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
import Utils
from sdkconfig import SdkConfig

def process_config(decompiledfoler, sdkfolder):
    Log.out("[Logging...] 拷贝资源文件 : [res]", True)
    if (os.path.exists(decompiledfoler) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % decompiledfoler, True)
        return False

    if (os.path.exists(sdkfolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % sdkfolder, True)
        return False

    configFile = os.path.join(sdkfolder, "sdk_config.xml")
    config = SdkConfig(configFile)
    copylist = config.getcopylist()
    if (copylist != None):
        for dir in copylist:
            file = os.path.join(sdkfolder, dir);
            dest = os.path.join(decompiledfoler, dir)
            if (os.path.isfile(file)):
                Utils.copyfile(file, dest)
            else:
                Utils.copydir(file, dest)
    return True