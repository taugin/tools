#!/usr/bin/python
# coding: UTF-8
import getopt
import subprocess
import sys
import os

OPEN_FOLDER = False
OPEN_GOOGLE_PLAY = False

def open_folder(args):
    path = None
    if len(args) > 0:
        path = os.path.abspath(args[0])
    else:
        path = os.getcwd()
    print("[Logging...] 打开文件路径 : [{}]".format(path))
    os.startfile(path)

def open_google_play(args):
    if len(args) > 0:
        package_name = args[0]
        install_referrer="https://play.google.com/store/apps/details?id={}&referrer=utm_source%3Dgoogle%26utm_medium%3Dcpc%26utm_term%3Dshoes%26utm_content%3Dlogolink%26utm_campaign%3Dspring_sale%26gclid%3Dadegadetwd3aer".format(package_name)
        #install_referrer="https://play.google.com/store/apps/details?id=com.simple.file.tool.browser&referrer=utm_source%3Dgoogle%26utm_medium%3Dcpc%26utm_term%3Daaaaaa%26anid%3Dadmob"
        print("[Logging...] 安装引荐网址 : {}".format(install_referrer))
        cmdlist = ['adb','shell','am', 'start','-a', 'android.intent.action.VIEW', '-d', install_referrer]
        subprocess.call(cmdlist)
    else:
        print("[Logging...] 缺少包名信息")

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "fg")
    for op, value in opts:
        if (op == "-f"):
            OPEN_FOLDER = True
        elif (op == '-g'):
            OPEN_GOOGLE_PLAY = True
        else:
            OPEN_FOLDER = True
    if OPEN_FOLDER:
        open_folder(args)
    elif OPEN_GOOGLE_PLAY:
        open_google_play(args)