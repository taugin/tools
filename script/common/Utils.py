#!/usr/bin/python
# coding: UTF-8

import os
import shutil

def copydir(fromdir, todir):
    list = os.walk(fromdir, True)
    for root, dirs, files in list:
        for file in files:
            todirname = root.replace(fromdir, todir)
            if (os.path.exists(todirname) == False):
                os.makedirs(todirname)
            #sdk文件夹内的文件
            fromdirfile = os.path.join(root, file)
            todirfile = fromdirfile.replace(fromdir, todir)
            #print(fromdirfile + " : " + todirfile)
            copyfile(fromdirfile, todirfile)

def copyfile(fromfile, tofile):
    try:
        shutil.copy2(fromfile, tofile)
    except:
        pass