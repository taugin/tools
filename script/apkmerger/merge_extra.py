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

def move_app_file(masterfolder, app_name):
    if (app_name == None or len(app_name) <= 0):
        return

    app_short_file = app_name.replace(".", os.sep)

    app_file = os.path.join(masterfolder, "smali", app_short_file + ".smali")
    exist = os.path.exists(app_file)
    if (exist):
        return

    app_file = os.path.join(masterfolder, "smali_classes2", app_short_file + ".smali")
    exist = os.path.exists(app_file)
    if (exist):
        copy_app_relative_files(masterfolder, "smali_classes2", app_short_file)
        return

    app_file = os.path.join(masterfolder, "smali_classes3", app_short_file + ".smali")
    exist = os.path.exists(app_file)
    if (exist):
        copy_app_relative_files(masterfolder, "smali_classes3", app_short_file)
        return

def copy_app_relative_files(masterfolder, smali, app_short_file):
    app_folder = os.path.dirname(os.path.join(masterfolder, smali, app_short_file))
    toroot = os.path.join(masterfolder, "smali")
    toroot = os.path.normpath(toroot)
    fromroot = os.path.join(masterfolder, smali)
    fromroot = os.path.normpath(fromroot)
    mylist = os.walk(app_folder, True)
    for root, filedir, files in mylist:
        for file in files:
            fromfile = os.path.join(root, file)
            fromfile = os.path.normpath(fromfile)

            tofile = fromfile.replace(fromroot, toroot)
            tofile = os.path.normpath(tofile)
            app_short_file = os.path.normpath(app_short_file)
            if (app_short_file in tofile):
                Utils.copyfile(fromfile, tofile, False)

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
    move_app_file(masterfolder, app_name)
    set_application(masterfolder, app_name)

if __name__ == "__main__":
    add_application("d:\\temp\\loseweight", "d:\\temp\\app-release-unsigned")
