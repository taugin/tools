#!/usr/bin/python
# coding: UTF-8

import _config
import Common
import Utils

import os
import xml.etree.ElementTree as ET

class ApkConfig:
    def __init__(self, channelList = [], globalPlugins = [], srcapk = None, finalname = None):
        self.channelList = []
        self.globalPlugin = []
        self.srcapk = srcapk
        self.finalname = finalname

        if (channelList != None):
            self.channelList = channelList

        if (globalPlugins != None):
            self.globalPlugins = globalPlugins

    def parse(self, configfile):
        if not os.path.exists(configfile):
            return
        tree = ET.parse(configfile)
        root = tree.getroot()
        srcapknode = root.find("srcapk")
        if (srcapknode != None):
            self.srcapk = srcapknode.text

        finalnamenode = root.find("finalname")
        if (finalnamenode != None):
            self.finalname = finalnamenode.text

        globalPlugin = root.findall("global-plugins/plugin")
        mydict = {}
        for plugin in globalPlugin:
            mydict["name"] = plugin.attrib["name"]
            mydict["desc"] = plugin.attrib["desc"]
            self.globalPlugin += [mydict]

        allchannels = root.findall("channels/channel")
        for channel in allchannels:
            sdkChannel = Channel(globalPlugins = self.globalPlugins)
            self.channelList.append(sdkChannel)
            sdkChannel.parse(channel)

    def getChannelList(self):
        return self.channelList

    def getGlobalPlugin(self):
        return self.globalPlugin

    def getsrcapk(self):
        return self.srcapk

    def getfinalname(self):
        return self.finalname

class Channel:
    def __init__(self, properties = None,
                  manifest = None, plugins = None, globalPlugins = None,
                  baseParams = None, channelParams = None,
                  versionParams = None, keystoreinfo = None,
                  spec_params = None):
        #developer_config.properties文件配置
        self.properties = []
        #manifest meta信息
        self.manifest = []
        #渠道插件
        self.plugins = []
        #全局插件
        self.globalPlugins = []
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


        if properties != None:
            self.properties = properties

        if manifest != None:
            self.manifest = manifest

        if plugins != None:
            self.plugins = plugins

        if globalPlugins != None:
            self.globalPlugins = globalPlugins

        if baseParams != None:
            self.baseParams = baseParams

        if channelParams != None:
            self.channelParams = channelParams

        if versionParams != None:
            self.versionParams = versionParams

        if keystoreinfo != None:
            self.keystoreinfo = keystoreinfo

        if spec_params != None:
            self.spec_params = spec_params

    #解析
    def parse(self, root):
        self._parseChannel(root)
        self._parseKeystore()

    #解析渠道
    def _parseChannel(self, root):
        #获取params
        params = root.findall("param")
        if (params != None):
            for param in params:
                self.baseParams[Utils.getattrib(param, "name")] = Utils.getattrib(param, "value")

        #获取渠道配置参数
        sdkparams = root.findall("sdk/param")
        if (sdkparams != None):
            for param in sdkparams:
                self.channelParams[Utils.getattrib(param, "name")] = Utils.getattrib(param, "value")

        #获取版本参数
        verCode = root.find("sdk-version/versionCode")
        verName = root.find("sdk-version/versionName")
        if (verCode != None):
            self.channelParams["vercode"] = verCode.text
        if (verName != None):
            self.channelParams["vername"] = verName.text

        #获取properties
        properties = root.findall("properties/param")
        for sdkp in properties:
            mydict = {}
            mydict["name"] = Utils.getattrib(sdkp, "name")
            mydict["value"] = Utils.getattrib(sdkp, "value")
            mydict["desc"] = Utils.getattrib(sdkp, "desc")
            self.properties += [mydict]

        #获取manifest
        manifest = root.findall("manifest/param")
        for sdkp in manifest:
            mydict = {}
            mydict["name"] = Utils.getattrib(sdkp, "name")
            mydict["value"] = Utils.getattrib(sdkp, "value")
            mydict["desc"] = Utils.getattrib(sdkp, "desc")
            self.manifest += [mydict]

        #获取spec-params
        specparams = root.findall("spec-params/param")
        for sdkp in specparams:
            mydict = {}
            mydict["name"] = Utils.getattrib(sdkp, "name")
            mydict["value"] = Utils.getattrib(sdkp, "value")
            self.spec_params += [mydict]

        plugins = root.findall("plugins/plugin")
        for plugin in plugins:
            mydict = {}
            mydict["name"] = Utils.getattrib(plugin, "name")
            mydict["desc"] = Utils.getattrib(plugin, "desc")
            self.plugins += [mydict]

    #解析渠道签名
    def _parseKeystore(self):
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
        return self.plugins + self.globalPlugins

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
