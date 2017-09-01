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

import subprocess


def apktool_cmd():
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR]
    cmdlist += sys.argv[1:]
    subprocess.call(cmdlist)

apktool_cmd()
Common.pause()