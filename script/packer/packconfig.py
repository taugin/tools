#!/usr/bin/python
# coding: UTF-8

import moduleconfig
import Common
import Utils

import os
import xml.etree.ElementTree as ET

class PackConfig:
    def __init__(self, configfile):
        tree = ET.parse(configfile)
        self.root = tree.getroot()
        self.channelList = []
        self.globalPlugin = []
        self.signapkinfo = {}
        self.srcapk = None

    def parse(self):
        srcapknode = self.root.find("srcapk")
        if (srcapknode != None):
            self.srcapk = srcapknode.text

        globalPlugin = self.root.findall("global-plugins/plugin")
        mydict = {}
        for plugin in globalPlugin:
            mydict["name"] = plugin.attrib["name"]
            mydict["desc"] = plugin.attrib["desc"]
            self.globalPlugin += [mydict]

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

    def getsrcapk(self):
        return self.srcapk

class Channel:
    def __init__(self, root, globalPlugin):
        #developer_config.properties文件配置
        self.properties = []
        #manifest meta信息
        self.manifest = []
        #渠道插件
        self.plugins = []
        #全局插件
        self.globalPugins = globalPlugin
        #基本参数
        self.map = {}
        self.root = root
        #签名信息
        self.keystoreinfo = {}

        self.parseChannel()
        self.parseKeystore()

    #解析渠道
    def parseChannel(self):
        #获取params
        params = self.root.findall("param")
        if (params != None):
            for param in params:
                self.set(Utils.getattrib(param, "name"), Utils.getattrib(param, "value"))

        verCode = self.root.find("sdk-version/versionCode")
        verName = self.root.find("sdk-version/versionName")
        if (verCode != None):
            self.set("vercode", verCode.text);
        if (verName != None):
            self.set("vername", verName.text);
        #获取properties
        properties = self.root.findall("properties/param")
        for sdkp in properties:
            mydict = {}
            mydict["name"] = Utils.getattrib(sdkp, "name")
            mydict["value"] = Utils.getattrib(sdkp, "value")
            mydict["desc"] = Utils.getattrib(sdkp, "desc")
            self.properties += [mydict]

        #获取manifest
        manifest = self.root.findall("manifest/param")
        for sdkp in manifest:
            mydict = {}
            mydict["name"] = Utils.getattrib(sdkp, "name")
            mydict["value"] = Utils.getattrib(sdkp, "value")
            mydict["desc"] = Utils.getattrib(sdkp, "desc")
            self.manifest += [mydict]

        plugins = self.root.findall("plugins/plugin")
        for plugin in plugins:
            mydict = {}
            mydict["name"] = Utils.getattrib(plugin, "name")
            mydict["desc"] = Utils.getattrib(plugin, "desc")
            self.plugins += [mydict]

    #解析渠道签名
    def parseKeystore(self):
        keystore = os.path.join(Common.SDK_DIR, "keystore/keystore.xml")
        if (os.path.exists(keystore) == False):
            return
        tree = ET.parse(keystore)
        root = tree.getroot()
        channel = root.find(".//keystores/keystore[@channel='%s']" % self.getsdkname())
        if (channel == None):
            channel = root.find(".//keystores/keystore[@channel='default']")
        if (channel == None):
            return
        params = channel.findall("param")
        if (params == None):
            return
        for p in params:
            self.keystoreinfo[p.attrib["name"]] = p.attrib["value"]

    def set(self, key, value):
        self.map[key] = value

    def getProperties(self):
        return self.properties

    def getManifest(self):
        return self.manifest

    def getPlugin(self):
        return self.plugins + self.globalPugins

    def getsdkid(self):
        return Utils.getvalue(self.map, "id")

    def getsdkname(self):
        return Utils.getvalue(self.map, "name")

    def getsdkdir(self):
        return Utils.getvalue(self.map, "sdk")

    def getsdkdesc(self):
        return Utils.getvalue(self.map, "desc")

    def getsdksuffix(self):
        return Utils.getvalue(self.map, "suffix")

    def isSplash(self):
        tmp = Utils.getvalue(self.map, "splash")
        if (tmp != None and tmp != "0"):
            return True
        else:
            return False

    def isUnitySplash(self):
        tmp = Utils.getvalue(self.map, "unity_splash")
        if (tmp != None and tmp != "0"):
            return True
        else:
            return False

    def getsdkicon(self):
        return Utils.getvalue(self.map, "icon")

    def getfinalname(self):
        return Utils.getvalue(self.map, "finalname")

    def getvercode(self):
        return Utils.getvalue(self.map, "vercode")

    def getvername(self):
        return Utils.getvalue(self.map, "vername")

    def getkeystore(self):
        return self.keystoreinfo

    def getcornerpos(self):
        return Utils.getvalue(self.map, "corner")
