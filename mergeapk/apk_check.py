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

def activity_check(payfolder):
    paymanifest = "%s/AndroidManifest.xml" % payfolder;
    ET.register_namespace('android', XML_NAMESPACE)
    paytree = ET.parse(paymanifest)
    payroot = paytree.getroot()
    cocospay_activity = payroot.find(".//activity/[@{%s}name='%s']" % (XML_NAMESPACE, COCOSPAY_ACTIVITY))
    if (cocospay_activity != None):
        return True
    else:
        return False

def service_check(payfolder):
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
    activitycheck = activity_check(payfolder)
    servicecheck = service_check(payfolder)
    finalcheck =  activitycheck and servicecheck
    if (finalcheck == False):
        if (activitycheck == False):
            log("[Logging...] 缺失 [%s]" % COCOSPAY_ACTIVITY)
        if (servicecheck == False):
            log("[Logging...] 缺失 [%s]" % COCOSPAY_SERVICE)
    log("[Logging...] 检测完成\n")
    return finalcheck

if (__name__ == "__main__"):
    apk_check(sys.argv[1], sys.argv[2])