#!/usr/bin/python
# coding: UTF-8
'''
配置文件模板
<?xml version='1.0' encoding='utf-8'?>
<config>
    <merge>
        <gameapk>HomeCP_R_2015-07-06-14-58-52_v3.0.0.apk</gameapk>
        <payapk>E:\CkSourceCode\CocosPaySdk\release\MM-release-unsigned.apk</payapk>
        <package></package>
        <output>mm.apk</output>
        <company>上海触控</company>
    </merge>
    <merge>
        <gameapk>HomeCP_R_2015-07-06-14-58-52_v3.0.0.apk</gameapk>
        <payapk>E:\CkSourceCode\CocosPaySdk\release\MM-release-unsigned.apk</payapk>
        <package></package>
        <output>mm.apk</output>
        <company>上海触控</company>
    </merge>
</config>
'''
import os
import re
import subprocess
import sys
import threading

import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

CONFIG_FILE = "config.xml"
PERMISSIONS = "permissions.xml"

def log(str, show=True):
    if (show):
        print(str)

class ConfigParer:
    root = None
    instance = None
    mutex = threading.Lock()

    @staticmethod
    def getInstance():
        if(ConfigParer.instance == None):
            ConfigParer.mutex.acquire()
            if(ConfigParer.instance == None):
                ConfigParer.instance = ConfigParer()
            ConfigParer.mutex.release()
        return ConfigParer.instance

    def __init__(self):
        if (os.path.exists(CONFIG_FILE)):
            try:
                tree = ET.parse(CONFIG_FILE)
                ConfigParer.root = tree.getroot()
            except:
                log("[Logging...] 解析文件出错 : [%s]" % CONFIG_FILE, True)

    def readconfig(self, tag):
        if (ConfigParer.root != None):
            element = ConfigParer.root.find(tag)
            if (element != None):
                return element.text;
        return None

    def readpkglist(self):
        list = []
        if (ConfigParer.root != None):
            pkgs = ConfigParer.root.findall("merge")
            for pkg in pkgs:
                dict = {}
                gameapk = pkg.find("gameapk")
                if (gameapk != None):
                    dict["gameapk"] = gameapk.text
                payapk = pkg.find("payapk")
                if (payapk != None):
                    dict["payapk"] = payapk.text
                package = pkg.find("package")
                if (package != None):
                    dict["package"] = package.text
                company = pkg.find("company")
                if (company != None):
                    dict["company"] = company.text
                output = pkg.find("output")
                if (output != None):
                    dict["output"] = output.text
                list += [dict]
        return list

def readmergelist():
    config_parser = ConfigParer.getInstance()
    return config_parser.readpkglist()

'''
<permissions>
    <permission>android.intent.action.SEND_SMS</permisssion>
</permissions>
'''
class PermissionParer:
    root = None
    instance = None
    mutex = threading.Lock()

    @staticmethod
    def getInstance():
        if(PermissionParer.instance == None):
            PermissionParer.mutex.acquire()
            if(PermissionParer.instance == None):
                PermissionParer.instance = PermissionParer()
            PermissionParer.mutex.release()
        return PermissionParer.instance

    def __init__(self):
        if (os.path.exists(PERMISSIONS)):
            try:
                tree = ET.parse(PERMISSIONS)
                PermissionParer.root = tree.getroot()
            except:
                log("[Logging...] 解析文件出错 : [%s]" % PERMISSIONS, True)

    def getlist(self):
        list = []
        if (PermissionParer.root != None):
            allElement = PermissionParer.root.findall("permission")
            if (allElement != None):
                for element in allElement:
                    list += [element.text]
        return list

def get_sensitive_permissions():
    permissionParser = PermissionParer.getInstance()
    list = permissionParser.getlist()
    return list