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


class SdkConfig:
    def __init__(self, config):
        tree = ET.parse(config)
        self.root = tree.getroot()

    def getattrib(self, item, attr):
        try:
            return item.attrib[attr]
        except:
            return None
        
    def getsdkname(self):
        if (self.root != None):
            element = self.root.find("name")
            if (element != None):
                return element.text;
        return None

    def getsdkvcode(self):
        if (self.root != None):
            element = self.root.find("version/versionCode")
            if (element != None):
                return element.text;
        return None

    def getsdkvname(self):
        if (self.root != None):
            element = self.root.find("version/versionName")
            if (element != None):
                return element.text;
        return None

    def getplugins(self):
        list = []
        if (self.root != None):
            plugins = self.root.findall("plugins/plugin")
            if (plugins != None):
                for plugin in plugins:
                    list += [plugin]
        return list

    def getparams(self):
        list = []
        if (self.root != None):
            params = self.root.findall("params/param")
            if (params != None):
                for param in params:
                    dict = {}
                    if (param != None):
                        dict["name"] = self.getattrib(param, "name")
                        dict["type"] = self.getattrib(param, "type")
                    list += [dict]
        return list

    def getcopylist(self):
        list = []
        if (self.root != None):
            params = self.root.findall("copylist/param")
            if (params != None):
                for param in params:
                    if (param != None):
                        list += [param.text]
        return list

    def process_config(self, decompiledfolder, sdkfolder):
        Log.out("[Logging...] 拷贝资源文件 : [res]", True)
        if (os.path.exists(decompiledfolder) == False):
            Log.out("[Error...] 无法定位文件夹 %s" % decompiledfolder, True)
            return False
    
        if (os.path.exists(sdkfolder) == False):
            Log.out("[Error...] 无法定位文件夹 %s" % sdkfolder, True)
            return False
    
        copylist = self.getcopylist()
        if (copylist != None):
            for d in copylist:
                file = os.path.join(sdkfolder, d);
                dest = os.path.join(decompiledfolder, d)
                if (os.path.isfile(file)):
                    Utils.copyfile(file, dest)
                else:
                    Utils.copydir(file, dest)
        Log.out("[Logging...] 拷贝资源完成\n", True)
        return True

    def process_plugin(self, decompiledfolder, sdkfolder):
        pluginfile = os.path.join(decompiledfolder, "assets", "plugin_config.xml")
        if (os.path.exists(pluginfile) == False):
            self.create_plugin(pluginfile)

        self.append_plugin(pluginfile)
    def append_plugin(self, pluginfile):
        Log.out("[Logging...] 添加插件文件");
        tree = ET.parse(pluginfile)
        root = tree.getroot()
        pluginlist = self.getplugins()
        if (len(pluginlist) > 0):
            for p in pluginlist:
                root.append(p)
            Utils.indent(root)
            tree.write(pluginfile, encoding='utf-8')

    def create_plugin(self, pluginfile):
        Log.out("[Logging...] 创建插件文件");
        doc = Document()  #创建DOM文档对象
        root = doc.createElement('plugins') #创建根元素
        doc.appendChild(root)
        f = open(pluginfile,'wb')
        f.write(doc.toxml(encoding = "utf-8"))
        f.close()