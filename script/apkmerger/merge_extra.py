#!/usr/bin/python
# coding: UTF-8
# encoding:utf-8
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

import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document
###########################################################################

'''
拷贝指定前缀的文件到smali文件夹对应的位置
'''
def move_special_files(masterfolder, prefix):
    fromdir = os.path.normpath("%s/smali_classes2" % masterfolder)
    dstdir = os.path.normpath("%s/smali" % masterfolder)
    if (os.path.exists(fromdir) and os.path.exists(dstdir)):
        filelist = os.walk(fromdir, True)
        for root, filedir, files in filelist:
            for file in files:
                fromfile = os.path.join(root, file)
                tofile = fromfile.replace(fromdir, dstdir)
                if (os.path.exists(fromfile) and prefix in fromfile):
                    Utils.movefile(fromfile, tofile)

    fromdir = os.path.normpath("%s/smali_classes3" % masterfolder)
    dstdir = os.path.normpath("%s/smali" % masterfolder)
    if (os.path.exists(fromdir) and os.path.exists(dstdir)):
        filelist = os.walk(fromdir, True)
        for root, filedir, files in filelist:
            for file in files:
                fromfile = os.path.join(root, file)
                tofile = fromfile.replace(fromdir, dstdir)
                if (os.path.exists(fromfile) and prefix in fromfile):
                    Utils.movefile(fromfile, tofile)

'''
增加application文件
'''
def get_application_name(slavefolder):
    manifest = os.path.join(slavefolder, "AndroidManifest.xml")
    tree = ET.parse(manifest)
    root = tree.getroot()
    package = root.get("package")
    application = root.find("application")
    app_name = application.get("{%s}name" % Common.XML_NAMESPACE)
    if (app_name != None and app_name.startswith(".")):
        app_name = package + app_name
    return app_name;

def has_application(masterfolder):
    manifest = os.path.join(masterfolder, "AndroidManifest.xml")
    tree = ET.parse(manifest)
    root = tree.getroot()
    application = root.find("application")
    app_name = application.get("{%s}name" % Common.XML_NAMESPACE)
    if (app_name != None and len(app_name) > 0):
        return True
    return False

def set_application(masterfolder, app_name):
    manifest = os.path.join(masterfolder, "AndroidManifest.xml")
    tree = ET.parse(manifest)
    ET.register_namespace('android', Common.XML_NAMESPACE)
    root = tree.getroot()
    application = root.find("application")
    application.set("{%s}name" % Common.XML_NAMESPACE, app_name)
    tree.write(manifest, encoding='utf-8', xml_declaration=True)

def add_application(masterfolder, slavefolder):
    has_app = has_application(masterfolder)
    if (has_app):
        return
    app_name = get_application_name(slavefolder)
    if (app_name == None or len(app_name) <= 0):
        return
    set_application(masterfolder, app_name)
###########################################################################
#查找原插件app中的启动Activity
ENTRY_ACTIVITY_XPATH = ".//meta-data/[@{%s}name='new_entry']/.." % (Common.XML_NAMESPACE)
LAUNCHER_ACTIVITY_XPATH = "intent-filter/category/[@{%s}name='android.intent.category.LAUNCHER']/.." % Common.XML_NAMESPACE
def find_launcher_activity(root):
    entryNode = root.find(Common.MAIN_ACTIVITY_XPATH)
    if (entryNode != None):
        return entryNode

''' 找出有<meta-data android:name="entry_activity" android:value="true"/>的activity'''
def find_entry_activity(masterroot, slaveroot):
    entryNode = slaveroot.find(ENTRY_ACTIVITY_XPATH)
    if (entryNode != None):
        activity_name = entryNode.get("{%s}name" % Common.XML_NAMESPACE)
        if activity_name != None and len(activity_name):
            activity_node = masterroot.find(".//activity/[@{%s}name='%s']" % (Common.XML_NAMESPACE, activity_name))
            return activity_node
    return None

def modify_entry_activity(package_name, app_launcher_activity, new_entry_activity):
    if (app_launcher_activity == None or new_entry_activity == None or package_name == None):
        return
    launcher_full_name = app_launcher_activity.get("{%s}name" % Common.XML_NAMESPACE)
    if (launcher_full_name == None):
        return
    if (launcher_full_name.startswith(".")):
        launcher_full_name = package_name + launcher_full_name

    entry_full_name = new_entry_activity.get("{%s}name" % Common.XML_NAMESPACE)
    if (entry_full_name == None):
        return
    if (entry_full_name.startswith(".")):
        entry_full_name = package_name + entry_full_name
    if (launcher_full_name == entry_full_name):
        return
    intentFilterNode = app_launcher_activity.find(LAUNCHER_ACTIVITY_XPATH)
    if intentFilterNode != None:
        app_launcher_activity.remove(intentFilterNode)
        if (new_entry_activity.find(LAUNCHER_ACTIVITY_XPATH) == None):
            new_entry_activity.append(intentFilterNode)
        element = ET.Element("meta-data")
        element.set("{%s}name" % Common.XML_NAMESPACE, "app_entry_name")
        element.set("{%s}value" % Common.XML_NAMESPACE, launcher_full_name)
        new_entry_activity.append(element)

def modify_activity_entry(masterfolder, slavefolder):
    if (os.path.exists(masterfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % masterfolder, True)
        sys.exit(0)
    if (os.path.exists(slavefolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % slavefolder, True)
        sys.exit(0)
    mastermanifest = "%s/AndroidManifest.xml" % masterfolder;
    slavemanifest = "%s/AndroidManifest.xml" % slavefolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    mastertree = ET.parse(mastermanifest)
    masterroot = mastertree.getroot()

    slavetree = ET.parse(slavemanifest)
    slaveroot = slavetree.getroot()

    package_name = masterroot.get("package")
    app_launcher_activity = find_launcher_activity(masterroot)
    new_entry_activity = find_entry_activity(masterroot, slaveroot)
    modify_entry_activity(package_name, app_launcher_activity, new_entry_activity)
    Utils.indent(masterroot)
    mastertree.write(mastermanifest, encoding="utf-8", xml_declaration=True)

###########################################################################
def merge_extra(masterfolder, slavefolder):
    add_application(masterfolder, slavefolder)
    modify_activity_entry(masterfolder, slavefolder)
    move_special_files(masterfolder, os.path.normpath("com/wb/rpadapter"))

if __name__ == "__main__":
    move_special_files("d:\\temp\\loseweight", os.path.normpath("com/wb/rpadapter"))
