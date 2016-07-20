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

import shutil

def should_copysdkfile(name):
    if (name.startswith("res")):
        return False
    if (name.startswith("AndroidManifest.xml")):
        return False
    if (name.startswith("classes.dex")):
        return False
    if (name.startswith("sdk_config.xml")):
        return False
    return True

#合并资源文件
def copy_res(decompiledfoler, sdkfolder):

    gameres = os.path.join(decompiledfoler, "res")
    sdkres = os.path.join(sdkfolder, "res")

    list = os.walk(sdkres, True)
    for root, dirs, files in list:
        for file in files:
            game_dir = root.replace(sdkfolder, decompiledfoler)
            if (os.path.exists(game_dir) == False):
                os.makedirs(game_dir)

            #sdk文件夹内的文件
            sdkfile = os.path.join(root, file)

            #除res/values文件夹外，其余资源直接拷贝
            if (root.endswith("values") == False):
                gamefile = sdkfile.replace(sdkfolder, decompiledfoler)
                shutil.copy2(sdkfile, gamefile)
            else: #res/values/文件夹内的文件，添加abch_前缀后，再拷贝
                if (file != "public.xml"):
                    file = "abch_" + file
                    tmp = os.path.join(root, file)
                    gamefile = tmp.replace(sdkfolder, decompiledfoler)
                    shutil.copy2(sdkfile, gamefile)
    Log.out("[Logging...] 拷贝资源完成\n", True)
    return True

def copy_leftfiles(decompiledfoler, sdkfolder):
    sdkfileslist = os.walk(sdkfolder, True)
    for root, dirs, files in sdkfileslist:
        for file in files:
            if (should_copysdkfile(root) == False):
                continue

            game_dir = root.replace(sdkfolder, decompiledfoler)
            if (os.path.exists(game_dir) == False):
                os.makedirs(game_dir)

            #sdk文件夹内的文件
            sdkfile = os.path.join(root, file)

            #除res/values文件夹外，其余资源直接拷贝
            gamefile = sdkfile.replace(sdkfolder, decompiledfoler)
            shutil.copy2(sdkfile, gamefile)
    Log.out("[Logging...] 拷贝资源完成\n", True)
    return True

def copy_sdkfiles(decompiledfoler, sdkfolder):
    Log.out("[Logging...] 拷贝资源文件 : [res]", True)
    if (os.path.exists(decompiledfoler) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % decompiledfoler, True)
        return False

    if (os.path.exists(sdkfolder) == False):
        Log.out("[Error...] 无法定位文件夹 %s" % sdkfolder, True)
        return False

    return copy_res(decompiledfoler, sdkfolder) and copy_leftfiles(decompiledfoler, sdkfolder)