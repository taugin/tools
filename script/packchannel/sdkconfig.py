#!/usr/bin/python
# coding: UTF-8

import moduleconfig
import Log
import Utils

import os
import xml.etree.ElementTree as ET
#from xml.etree import cElementTree as ET
#from xml.dom import minidom
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
        mylist = []
        if (self.root != None):
            plugins = self.root.findall("plugins/plugin")
            if (plugins != None):
                for plugin in plugins:
                    mylist += [plugin]
        return mylist

    def getparams(self):
        mylist = []
        if (self.root != None):
            params = self.root.findall("params/param")
            if (params != None):
                for param in params:
                    mydict = {}
                    if (param != None):
                        mydict["name"] = self.getattrib(param, "name")
                        mydict["type"] = self.getattrib(param, "type")
                    mylist += [mydict]
        return mylist

    def getcopylist(self):
        mylist = []
        if (self.root != None):
            params = self.root.findall("copylist/param")
            if (params != None):
                for param in params:
                    if (param != None):
                        mylist += [param.text]
        return mylist

    def process_config(self, decompiledfolder, sdkfolder):
        Log.out("[Logging...] 拷贝资源文件 ", True)
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
                Log.out("[Logging...] 正在拷贝文件  : [%s]" % d)
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