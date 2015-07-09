#!/usr/bin/python
# coding: UTF-8

import os
import sys
import xml.etree.ElementTree as ET

XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

COCOSPAY_ACTIVITY = "com.cocospay.CocosPayActivity"
COCOSPAY_SERVICE = "com.cocospay.CocosPayService"

def log(str, show=True):
    if (show):
        print(str)

def gameapk_axml_check(gamefolder):
    gamemanifest = "%s/AndroidManifest.xml" % gamefolder;
    ET.register_namespace('android', XML_NAMESPACE)
    gametree = ET.parse(gamemanifest)
    gameroot = gametree.getroot()
    cocospay_activity = gameroot.find(".//activity/[@{%s}name='%s']" % (XML_NAMESPACE, COCOSPAY_ACTIVITY))
    if (cocospay_activity != None):
        return True
    else:
        return False

def payapk_axml_check(payfolder):
    paymanifest = "%s/AndroidManifest.xml" % payfolder;
    ET.register_namespace('android', XML_NAMESPACE)
    paytree = ET.parse(paymanifest)
    payroot = paytree.getroot()
    cocospay_service = payroot.find(".//service/[@{%s}name='%s']" % (XML_NAMESPACE, COCOSPAY_SERVICE))
    if (cocospay_service != None):
        return True
    else:
        return False

def apk_check(gamefolder, payfolder):
    log("[Logging...] 关键组件检测")
    gamecheck = gameapk_axml_check(gamefolder)
    paycheck = payapk_axml_check(payfolder)
    finalcheck =  gamecheck and paycheck
    if (finalcheck == False):
        if (gamecheck == False):
            log("[Logging...] 缺失 [%s]" % COCOSPAY_ACTIVITY)
        if (paycheck == False):
            log("[Logging...] 缺失 [%s]" % COCOSPAY_SERVICE)
    log("[Logging...] 检测完成\n")
    return finalcheck

if (__name__ == "__main__"):
    apk_check(sys.argv[1], sys.argv[2])