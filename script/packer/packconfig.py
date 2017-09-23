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
        self.finalname = None

    def parse(self):
        srcapknode = self.root.find("srcapk")
        if (srcapknode != None):
            self.srcapk = srcapknode.text

        finalnamenode = self.root.find("finalname")
        if (finalnamenode != None):
            self.finalname = finalnamenode.text

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

    def getfinalname(self):
        return self.finalname

class Channel:
    def __init__(self, root, globalPlugin):
        self.root = root
        #developer_config.properties文件配置
        self.properties = []
        #manifest meta信息
        self.manifest = []
        #渠道插件
        self.plugins = []
        #全局插件
        self.globalPugins = globalPlugin
        #基本参数
        self.baseParams = {}
        #渠道参数
        self.channelParams = {}
        #版本参数
        self.versionParams = {}
        #签名信息
        self.keystoreinfo = {}
        #渠道自定义参数
        self.spec_params = []

        self.parseChannel()
        self.parseKeystore()

    #解析渠道
    def parseChannel(self):
        #获取params
        params = self.root.findall("param")
        if (params != None):
            for param in params:
                self.baseParams[Utils.getattrib(param, "name")] = Utils.getattrib(param, "value")

        #获取渠道配置参数
        sdkparams = self.root.findall("sdk/param")
        if (params != None):
            for param in sdkparams:
                self.channelParams[Utils.getattrib(param, "name")] = Utils.getattrib(param, "value")

        #获取版本参数
        verCode = self.root.find("sdk-version/versionCode")
        verName = self.root.find("sdk-version/versionName")
        if (verCode != None):
            self.channelParams["vercode"] = verCode.text
        if (verName != None):
            self.channelParams["vername"] = verName.text

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

        #获取spec-params
        specparams = self.root.findall("spec-params/param")
        for sdkp in specparams:
            mydict = {}
            mydict["name"] = Utils.getattrib(sdkp, "name")
            mydict["value"] = Utils.getattrib(sdkp, "value")
            self.spec_params += [mydict]

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

    #获取渠道参数开始
    def getsdkid(self):
        return Utils.getvalue(self.channelParams, "id")

    def getsdkname(self):
        return Utils.getvalue(self.channelParams, "name")

    def getsdkdir(self):
        return Utils.getvalue(self.channelParams, "sdk")

    def getsdkdesc(self):
        return Utils.getvalue(self.channelParams, "desc")

    #基本参数
    def getsuffix(self):
        return Utils.getvalue(self.baseParams, "suffix")

    def getcornerpos(self):
        return Utils.getvalue(self.baseParams, "corner")

    def isSplash(self):
        tmp = Utils.getvalue(self.baseParams, "splash")
        if (tmp != None and tmp != "0"):
            return True
        else:
            return False

    def isUnitySplash(self):
        tmp = Utils.getvalue(self.baseParams, "unity_splash")
        if (tmp != None and tmp != "0"):
            return True
        else:
            return False

    #填充的developer.properties中的参数
    def getProperties(self):
        return self.properties

    #填充的AndroidManifest.xml中的参数
    def getManifest(self):
        return self.manifest

    #填充的插件的参数
    def getPlugin(self):
        return self.plugins + self.globalPugins

    #渠道定制参数
    def getSpecParams(self):
        return self.spec_params

    #版本参数
    def getvercode(self):
        return Utils.getvalue(self.channelParams, "vercode")

    def getvername(self):
        return Utils.getvalue(self.channelParams, "vername")

    #签名参数
    def getkeystore(self):
        return self.keystoreinfo
