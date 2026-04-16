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
OPEN_MARKET = False

def open_folder(args):
    path = None
    if len(args) > 0:
        path = os.path.abspath(args[0])
    else:
        path = os.getcwd()
    print(f"[Logging...] 打开文件路径 : [{path}]")
    os.startfile(path)

def open_google_play(args):
    if len(args) > 0:
        package_name = args[0]
        open_google_play_adb(package_name, OPEN_NON_ORGANIC)
    else:
        print("[Logging...] 缺少包名信息")
def open_google_play_adb(pkgname, nonOrganic):
    if pkgname != None and len(pkgname) > 0:
        if nonOrganic:
            utm_source = "google"
            utm_medium = "cpc"
            utm_term = "shoes"
            utm_content = "logolink"
            utm_campaign = "spring_sale"
            gclid = f"gclid_XcfYukmct3xyz"
            referrer_source = f"referrer=utm_source%3D{utm_source}%26utm_medium%3D{utm_medium}%26utm_term%3D{utm_term}%26utm_content%3D{utm_content}%26utm_campaign%3D{utm_campaign}%26gclid%3D{gclid}"
            referrer = urllib.parse.quote(referrer_source)
            url=f"https://play.app.goo.gl/?link=https://play.google.com/store/apps/details?id={pkgname}%26{referrer}"
            print(f"[Logging...] 安装引荐网址 : {url}")
            print(f"[Logging...] 安装归因参数 : {urllib.parse.unquote(referrer_source)}")
        else:
            url=f"https://play.google.com/store/apps/details?id={pkgname}"
            print(f"[Logging...] 安装引荐网址 : {url}")
        cmdlist = ['adb','shell','am', 'start','-a', 'android.intent.action.VIEW', '-d', url]
        subprocess.call(cmdlist)
    else:
        print("[Logging...] 缺少包名信息")

def open_market(args):
    if len(args) > 0:
        package_name = args[0]
        url=f"market://details?id={package_name}"
        print(f"[Logging...] 安装引荐网址 : {url}")
        cmdlist = ['adb','shell','am', 'start','-a', 'android.intent.action.VIEW', '-d', url]
        subprocess.call(cmdlist)
    else:
        print("[Logging...] 缺少包名信息")

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "fgnm")
    for op, value in opts:
        if (op == "-f"):
            OPEN_FOLDER = True
        elif (op == '-g'):
            OPEN_GOOGLE_PLAY = True
        elif (op == '-n'):
            OPEN_NON_ORGANIC = True
        elif (op == '-m'):
            OPEN_MARKET = True
        else:
            OPEN_FOLDER = True
    if OPEN_FOLDER:
        open_folder(args)
    elif OPEN_MARKET:
        open_market(args)
    elif OPEN_GOOGLE_PLAY:
        open_google_play(args)