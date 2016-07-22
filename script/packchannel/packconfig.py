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
        self.signapkinfo = {}
        self.gameapk = None

    def parse(self):
        gameapkele = self.root.find("gameapk")
        if (gameapkele != None):
            self.gameapk = gameapkele.text

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

    def getsignapkinfo(self):
        return self.signapkinfo

    def getgameapk(self):
        return self.gameapk

class Channel:
    def __init__(self, root, globalPlugin):
        self.properties = []
        self.plugins = []
        self.globalPugins = globalPlugin
        self.map = {}
        self.root = root
        self.keystoreinfo = {}
        self.parseChannel()
        self.parseKeystore()

    #解析渠道
    def parseChannel(self):
        #获取params
        params = self.root.findall("param")
        if (params != None):
            for param in params:
                self.set(param.attrib["name"], param.attrib["value"])

        verCode = self.root.find("sdk-version/versionCode")
        verName = self.root.find("sdk-version/versionName")
        if (verCode != None):
            self.set("vercode", verCode.text);
        if (verName != None):
            self.set("vername", verName.text);
        #获取sdkparams
        properties = self.root.findall("properties/param")
        dict = {}
        for sdkp in properties:
            dict["name"] = sdkp.attrib["name"]
            dict["value"] = sdkp.attrib["value"]
            dict["desc"] = sdkp.attrib["desc"]
            self.properties += [dict]
        plugins = self.root.findall("plugins/plugin")
        dict = {}
        for plugin in plugins:
            dict["name"] = plugin.attrib["name"]
            dict["desc"] = plugin.attrib["desc"]
            self.plugins += [dict]

    #解析渠道签名
    def parseKeystore(self):
        keystore = os.path.join(Common.SDK, "keystore/keystore.xml")
        if (os.path.exists(keystore) == False):
            return
        tree = ET.parse(keystore)
        root = tree.getroot()
        channel = root.find(".//param[@name='channelName'][@value='%s']/.." % self.getsdkname())
        if (channel == None):
            return
        params = channel.findall("param")
        if (params == None):
            return
        for p in params:
            self.keystoreinfo[p.attrib["name"]] = p.attrib["value"]

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

    def getkeystore(self):
        return self.keystoreinfo
