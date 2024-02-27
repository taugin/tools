#!/usr/bin/python
# coding: UTF-8
import getopt
import subprocess
import sys
import os

import urllib.parse

OPEN_FOLDER = False
OPEN_GOOGLE_PLAY = False
OPEN_NON_ORGANIC = False

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
        if OPEN_NON_ORGANIC:
            utm_source = "google"
            utm_medium = "cpc"
            utm_term = "shoes"
            utm_content = "logolink"
            utm_campaign = "spring_sale"
            gclid = "adegadetwd3aer"
            referrer = "referrer=utm_source%3D{}%26utm_medium%3D{}%26utm_term%3D{}%26utm_content%3D{}%26utm_campaign%3D{}%26gclid%3D{}".format(utm_source, utm_medium, utm_term, utm_content, utm_campaign, gclid)
            referrer = urllib.parse.quote(referrer)
            url="https://play.app.goo.gl/?link=https://play.google.com/store/apps/details?id={}%26{}".format(package_name, referrer)
        else:
            url="https://play.google.com/store/apps/details?id={}".format(package_name)
        print("[Logging...] 安装引荐网址 : {}".format(url))
        cmdlist = ['adb','shell','am', 'start','-a', 'android.intent.action.VIEW', '-d', url]
        subprocess.call(cmdlist)
    else:
        print("[Logging...] 缺少包名信息")

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "fgn")
    for op, value in opts:
        if (op == "-f"):
            OPEN_FOLDER = True
        elif (op == '-g'):
            OPEN_GOOGLE_PLAY = True
        elif (op == '-n'):
            OPEN_NON_ORGANIC = True
        else:
            OPEN_FOLDER = True
    if OPEN_FOLDER:
        open_folder(args)
    elif OPEN_GOOGLE_PLAY:
        open_google_play(args)