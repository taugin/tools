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

import re
import subprocess
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document

class PackConfig:
    def __init__(self, configfile):
        tree = ET.parse(configfile)
        self.root = tree.getroot()
        self.channelList = []
        self.globalPlugin = []

    def parse(self):
        globalPlugin = self.root.findall("global-plugins/plugin")
        dict = {}
        for plugin in globalPlugin:
            dict["name"] = plugin.attrib["name"]
            dict["desc"] = plugin.attrib["desc"]
            self.globalPlugin += [dict]

        allchannels = self.root.findall("channels/channel")
        for channel in allchannels:
            sdkChannel = Channel(channel, self.globalPlugin)
            self.channelList += [sdkChannel]

    def getChannelList(self):
        return self.channelList

    def getGlobalPlugin(self):
        return self.globalPlugin

class Channel:
    def __init__(self, root, globalPlugin):
        self.sdkparams = []
        self.plugins = []
        self.globalPugins = globalPlugin
        self.map = {}

        #获取params
        params = root.findall("param")
        if (params != None):
            for param in params:
                self.set(param.attrib["name"], param.attrib["value"])

        verCode = root.find("sdk-version/versionCode")
        verName = root.find("sdk-version/versionName")
        if (verCode != None):
            self.set("vercode", verCode.text);
        if (verName != None):
            self.set("vername", verName.text);
        #获取sdkparams
        sdkparams = root.findall("sdk-params/param")
        dict = {}
        for sdkp in sdkparams:
            dict["name"] = sdkp.attrib["name"]
            dict["value"] = sdkp.attrib["value"]
            dict["desc"] = sdkp.attrib["desc"]
            self.sdkparams += [dict]
        plugins = root.findall("plugins/plugin")
        dict = {}
        for plugin in plugins:
            dict["name"] = plugin.attrib["name"]
            dict["desc"] = plugin.attrib["desc"]
            self.plugins += [dict]

    def getitem(self, key):
        try:
            return self.map[key]
        except:
            return ""

    def set(self, key, value):
        self.map[key] = value

    def getSdkParams(self):
        return self.sdkparams

    def getPlugin(self):
        return self.plugins + self.globalPugins

    def getsdkid(self):
        return self.getitem("id")

    def getsdkname(self):
        return self.getitem("name")

    def getsdkdir(self):
        return self.getitem("sdk")

    def getsdkdesc(self):
        return self.getitem("desc")

    def getsdksuffix(self):
        return self.getitem("suffix")

    def isSplash(self):
        tmp = self.getitem("splash")
        if (tmp != None and tmp != "0"):
            return True
        else:
            return False

    def isUnitySplash(self):
        tmp = self.getitem("unity_splash")
        if (tmp != None and tmp != "0"):
            return True
        else:
            return False

    def getsdkicon(self):
        return self.getitem("icon")

    def getgamename(self):
        return self.getitem("gamename")

    def getvercode(self):
        return self.getitem("vercode")

    def getvername(self):
        return self.getitem("vername")