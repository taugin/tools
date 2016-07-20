#!/usr/bin/python
# coding: UTF-8

import os
import re
import subprocess
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom


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
                    dict = {}
                    if (plugin != None):
                        dict["name"] = self.getattrib(plugin, "name")
                        dict["type"] = self.getattrib(plugin, "type")
                        dict["desc"] = self.getattrib(plugin, "desc")
                    list += [dict]
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