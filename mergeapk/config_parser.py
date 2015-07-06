#!/usr/bin/python
# coding: UTF-8


import os
import re
import subprocess
import sys
import threading

import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

CONFIG_FILE = "config.xml"

def log(str, show=True):
    if (show):
        print(str)
        
class ConfigParer:
    root = None
    instance = None
    mutex=threading.Lock()

    @staticmethod
    def getInstance():
        if(ConfigParer.instance==None):
            ConfigParer.mutex.acquire()
            if(ConfigParer.instance==None):
                ConfigParer.instance=ConfigParer()
            ConfigParer.mutex.release()
        return ConfigParer.instance

    def __init__(self):
        if (os.path.exists(CONFIG_FILE)):
            tree = ET.parse(CONFIG_FILE)
            ConfigParer.root = tree.getroot()

    def readconfig(self, tag):
        if (ConfigParer.root != None):
            return ConfigParer.root.find(tag).text;
        return None

def getpackage():
    config_parser = ConfigParer.getInstance()
    pkgname = config_parser.readconfig("package")
    return pkgname

def getcompany():
    config_parser = ConfigParer.getInstance()
    company = config_parser.readconfig("company")
    return company
