import os
import re
import subprocess
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET
from xml.dom import minidom

TMP_PROJECT = "PayApk"
TMP_NAME = "PayApk"
TMP_ACTIVITY = "PayActivity"
MANIFEST = "AndroidManifest.xml"
PERMISSION_FILE = "AndroidManifest.permission.txt"
ACTIVITY_FILE = "AndroidManifest.activity.txt"
XML_NAMESPACE = "http://schemas.android.com/apk/res/android"

'''
<config>
    <payapk name="gb.apk" filter="0|103,201$1">
        <path></path>
    </payapk>
    <payapk name="mm.apk">
        <path></path>
    </payapk>
</config>
'''
def log(str, show=True):
    if (show):
        print(str)

## Get pretty look
def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem

def clear_manifest():
    tree = ET.parse("%s/%s" % (TMP_PROJECT, MANIFEST))
    root = tree.getroot()
    application = root.find("application")
    if (application != None):
        application.clear()
    tree.write("%s/%s" % (TMP_PROJECT, MANIFEST))

def generate_android():
    cmdlist = ["android", "create", "project", "--target", "7", "--name", TMP_NAME, "--path", TMP_PROJECT, "--activity", TMP_ACTIVITY, "--package", "com.cocospay"]
    ret = subprocess.call(cmdlist, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if (ret == 0):
        shutil.rmtree("%s/src" % TMP_PROJECT, ignore_errors = True)
        shutil.rmtree("%s/res" % TMP_PROJECT, ignore_errors = True)
        os.makedirs("%s/src" % TMP_PROJECT)
        os.makedirs("%s/res" % TMP_PROJECT)
        clear_manifest()
        return True
    return False

def clear_project():
    shutil.rmtree(TMP_PROJECT, ignore_errors = True)

def copy_files(srclist, dstproject):
    for src in srclist:
        list = os.walk(src, True)
        for root, dirs, files in list:
            for file in files:
                srcfile = os.path.join(root, file)
                dstdir = root.replace(src, dstproject)
                dstfile = os.path.join(dstdir, file)
                if (os.path.exists(dstdir) == False):
                    os.makedirs(dstdir)
                shutil.copy2(srcfile, dstfile)

def copy_manifest(srclist, dstproject):
    ET.register_namespace('android', XML_NAMESPACE)
    dstTree = ET.parse("%s/%s" % (TMP_PROJECT, MANIFEST))
    dstRoot = dstTree.getroot()
    dstApp = dstRoot.find("application")
    for src in srclist:
        permission_file = os.path.join(src, PERMISSION_FILE)
        tree = ET.parse(permission_file)
        root = tree.getroot()
        for item in root:
            dstRoot.append(item)
        activity_file = os.path.join(src, ACTIVITY_FILE)
        tree = ET.parse(activity_file)
        root = tree.getroot()
        for item in root:
            dstApp.append(item)
    indent(dstRoot)
    dstTree.write("%s/%s" % (TMP_PROJECT, MANIFEST))

def build_apk(key):
    finafile = os.path.join(os.getcwd(), key)
    buildfile = os.path.join(TMP_PROJECT, "build.xml")
    cmdlist = ["ant", "debug", "-buildfile", buildfile, "-Dout.final.file=%s" % finafile]
    cmdstr = ""
    for cmd in cmdlist:
        cmdstr += cmd + " "
    log(cmdstr)
    subprocess.call(cmdlist, shell=False)

def add_filter(filter, apkfile):
    if (filter == None or filter == ""):
        return
    apkzip = zipfile.ZipFile(apkfile, "a")
    apkzip.writestr("assets/filter", filter)
    apkzip.close()
    
if __name__=="__main__":
    tree = ET.parse("config.xml")
    root = tree.getroot()
    all = []
    payapk = root.findall("payapk")
    for pay in payapk:
        dict = {}
        l = []
        finalapk = pay.get("name")
        if (finalapk != None and finalapk != ""):
            dict["name"] = finalapk
        filter = pay.get("filter")
        if (filter != None and filter != ""):
            dict["filter"] = filter
        paths = pay.findall("path")
        for path in paths:
            l += [path.text]
        dict["path"] = l
        all += [dict]
    for s in all:
        name = s.get("name")
        path = s.get("path")
        filter = s.get("filter")
        clear_project()
        generate_android()
        copy_files(path, TMP_PROJECT)
        copy_manifest(path, TMP_PROJECT)
        build_apk(name)
        add_filter(filter, name)
        clear_project()
