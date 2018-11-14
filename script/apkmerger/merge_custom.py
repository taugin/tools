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

def move_files_recursion(fromdir, prefix, dstdir, recursion):
    if (os.path.exists(fromdir) and os.path.exists(dstdir)):
            filelist = os.walk(fromdir, True)
            for root, filedir, files in filelist:
                for file in files:
                    fromfile = os.path.join(root, file)
                    tofile = fromfile.replace(fromdir, dstdir)
                    if (os.path.exists(fromfile) and prefix in fromfile):
                        if not recursion:
                            dirname = os.path.dirname(fromfile)
                            if not dirname.endswith(prefix):
                                continue
                        Utils.movefile(fromfile, tofile)

'''
拷贝指定前缀的文件到smali文件夹对应的位置
'''
def move_special_files(masterfolder, prefix, recursion = True):
    Log.out("[Logging...] 移动指定文件 : [%s]" % prefix)
    smalidirs = ["smali_classes2", "smali_classes3", "smali_classes4", "smali_classes5", "smali_classes6"]
    dstdir = os.path.normpath("%s/smali" % masterfolder)
    prefix = os.path.normpath(prefix)

    for smalidir in smalidirs:
        fromdir = os.path.join(masterfolder, smalidir)
        if os.path.exists(fromdir):
            move_files_recursion(fromdir, prefix, dstdir, recursion)
        else:
            break;
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
    Log.out("[Logging...] 设置应用入口 : [%s]" % app_name)
    set_application(masterfolder, app_name)
###########################################################################
#查找原插件app中的启动Activity
ENTRY_ACTIVITY_XPATH = ".//meta-data/[@{%s}name='app_entry_name']/.." % (Common.XML_NAMESPACE)
META_ACTIVITY_XPATH = ".//meta-data/[@{%s}name='app_entry_name']" % (Common.XML_NAMESPACE)
LAUNCHER_ACTIVITY_XPATH = "intent-filter/category/[@{%s}name='android.intent.category.LAUNCHER']/.." % Common.XML_NAMESPACE
def find_launcher_activity(root):
    entryNode = root.find(Common.MAIN_ACTIVITY_XPATH)
    if (entryNode != None):
        return entryNode

''' 找出有<meta-data android:name="app_entry_name" android:value="true"/>的activity'''
def find_activity_with_app_entry(masterroot):
    return masterroot.find(ENTRY_ACTIVITY_XPATH)

def modify_entry_activity(package_name, old_entry_activity, activity_with_app_entry):
    if (old_entry_activity == None or activity_with_app_entry == None or package_name == None):
        return
    launcher_full_name = old_entry_activity.get("{%s}name" % Common.XML_NAMESPACE)
    if (launcher_full_name == None):
        return
    if (launcher_full_name.startswith(".")):
        launcher_full_name = package_name + launcher_full_name

    entry_full_name = activity_with_app_entry.get("{%s}name" % Common.XML_NAMESPACE)
    if (entry_full_name == None):
        return
    if (entry_full_name.startswith(".")):
        entry_full_name = package_name + entry_full_name
    if (launcher_full_name == entry_full_name):
        return
    intentFilterNode = old_entry_activity.find(LAUNCHER_ACTIVITY_XPATH)
    if intentFilterNode != None:
        old_entry_activity.remove(intentFilterNode)
        meta_data = activity_with_app_entry.find(META_ACTIVITY_XPATH)
        if (meta_data != None):
            meta_data.set("{%s}value" % Common.XML_NAMESPACE, launcher_full_name)

def modify_activity_entry(masterfolder):
    if (os.path.exists(masterfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % masterfolder, True)
        sys.exit(0)
    mastermanifest = "%s/AndroidManifest.xml" % masterfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    mastertree = ET.parse(mastermanifest)
    masterroot = mastertree.getroot()

    package_name = masterroot.get("package")
    #此处会查找到第一个入口activity，刚好是原app的入口
    old_entry_activity = find_launcher_activity(masterroot)
    activity_with_app_entry = find_activity_with_app_entry(masterroot)

    '''输出log'''
    entry_full_name = None
    if (activity_with_app_entry != None):
        entry_full_name = activity_with_app_entry.get("{%s}name" % Common.XML_NAMESPACE)
        if (entry_full_name != None and entry_full_name.startswith(".")):
            entry_full_name = package_name + entry_full_name
    if (entry_full_name != None):
        Log.out("[Logging...] 修改界面入口 : [%s]" % entry_full_name)
    '''输出log'''

    modify_entry_activity(package_name, old_entry_activity, activity_with_app_entry)
    Utils.indent(masterroot)
    mastertree.write(mastermanifest, encoding="utf-8", xml_declaration=True)

def contain_special_path(spfolder, spfile):
    if (spfolder == None or len(spfolder) <= 0 or spfile == None or len(spfile) <= 0):
        return False
    for sp in spfolder:
        if (sp in spfile):
            return True
    return False

def update_duplicate_files(masterfolder, spfolder):
    Log.out("[Logging...] 更新指定文件 ")
    fromdir = os.path.normpath("%s/smali_classes2" % masterfolder)
    dstdir = os.path.normpath("%s/smali" % masterfolder)
    if (os.path.exists(fromdir) and os.path.exists(dstdir)):
        filelist = os.walk(fromdir, True)
        for root, filedir, files in filelist:
            for file in files:
                fromfile = os.path.join(root, file)
                tofile = fromfile.replace(fromdir, dstdir)
                if (os.path.exists(fromfile) and os.path.exists(tofile) and contain_special_path(spfolder, fromfile)):
                    Log.out("fromfile : %s" % fromfile)
                    Utils.movefile(fromfile, tofile)

    fromdir = os.path.normpath("%s/smali_classes3" % masterfolder)
    dstdir = os.path.normpath("%s/smali" % masterfolder)
    if (os.path.exists(fromdir) and os.path.exists(dstdir)):
        filelist = os.walk(fromdir, True)
        for root, filedir, files in filelist:
            for file in files:
                fromfile = os.path.join(root, file)
                tofile = fromfile.replace(fromdir, dstdir)
                if (os.path.exists(fromfile) and os.path.exists(tofile) and contain_special_path(spfolder, fromfile)):
                    Log.out("fromfile : %s" % fromfile)
                    Utils.movefile(fromfile, tofile)

###########################################################################
def move_file_by_appname(masterfolder, slavefolder):
    slavemanifest = "%s/AndroidManifest.xml" % slavefolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)
    slavetree = ET.parse(slavemanifest)
    if slavetree == None:
        return

    slaveroot = slavetree.getroot()
    if slaveroot == None:
        return

    application = slaveroot.find("application")
    if application == None:
        return

    app_name = application.get("{%s}name" % Common.XML_NAMESPACE)
    if app_name == None or len(app_name) <= 0:
        return

    index = app_name.rfind(".")
    if index < 0:
        return
    pkgpath = app_name[:index]
    pkgpath = pkgpath.replace(".", os.path.sep)
    move_special_files(masterfolder, pkgpath)

def merge_custom(masterfolder, slavefolder):
    add_application(masterfolder, slavefolder)
    modify_activity_entry(masterfolder)
    move_file_by_appname(masterfolder, slavefolder)
    Log.out("");

if __name__ == "__main__":
    move_special_files(sys.argv[1], sys.argv[2])