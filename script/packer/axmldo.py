#!/usr/bin/python
# coding: UTF-8
#引入别的文件夹的模块

import _config
import Common
import Log
import Utils


import os
import xml.etree.ElementTree as ET

###############################################################################

#查找应用图标
def parseIconName(iconNode):
    '''解析图标文件'''
    if (iconNode != None):
        return iconNode.split("/")[1]
    return None
#查找应用图标
def findApkIcon(decompiledfolder):
    '''从AndroidManifest.xml中查找应用图标名称'''
    if (os.path.exists(decompiledfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % decompiledfolder, True)
        return False
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)
    manifesttree = ET.parse(manifestfile)
    manifestroot = manifesttree.getroot()
    applicationNode = manifestroot.find("application")
    iconNode = applicationNode.get("{%s}icon" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parseIconName(iconNode)

    iconNode = applicationNode.get("{%s}logo" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parseIconName(iconNode)

    mainactivity = manifestroot.findall(Common.MAIN_ACTIVITY_XPATH)
    if (mainactivity == None or len(mainactivity) <= 0):
        return None

    iconNode = mainactivity[0].get("{%s}icon" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parseIconName(iconNode)

    iconNode = mainactivity[0].get("{%s}logo" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parseIconName(iconNode)
    return None

#查找入口Application
def findEntryApplication(decompiledfolder):
    '''从AndroidManifest.xml中查找应用图标名称'''
    if (os.path.exists(decompiledfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % decompiledfolder, True)
        return False
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)
    manifesttree = ET.parse(manifestfile)
    manifestroot = manifesttree.getroot()
    packageName = manifestroot.get("package")
    applicationNode = manifestroot.find("application")
    appName = applicationNode.get("{%s}name" % Common.XML_NAMESPACE)
    if (appName == None or appName.strip() == ""):
        return None
    if (appName.startswith(".")) :
        return packageName + appName
    return appName

#查找原插件app中的启动Activity
def findEntryActivity(root):
    entryNode = root.find(Common.MAIN_ACTIVITY_XPATH)
    if (entryNode != None):
        return entryNode

def processEntryActivity(decompiledfolder, approot, sdkroot):
    appEntryNode = findEntryActivity(approot)
    sdkEntryNode = findEntryActivity(sdkroot)

    appEntryActivity = None
    sdkEntryActivity = None

    if appEntryNode != None:
        appEntryActivity = appEntryNode.attrib['{%s}name' % Common.XML_NAMESPACE]
    if sdkEntryNode != None:
        sdkEntryActivity = sdkEntryNode.attrib['{%s}name' % Common.XML_NAMESPACE]

    if appEntryActivity != None and appEntryActivity != '' and sdkEntryActivity != None and sdkEntryActivity != '':
        intentFilterNode = appEntryNode.find("intent-filter/category/[@{%s}name='android.intent.category.LAUNCHER']/.." % Common.XML_NAMESPACE)
        categoryNode = intentFilterNode.find('category')
        if intentFilterNode != None and categoryNode != None:
            intentFilterNode.remove(categoryNode)
            package = approot.get("package")
            if appEntryActivity.startswith("."):
                appEntryActivity = package + appEntryActivity
    return appEntryActivity, sdkEntryActivity

#添加入口activity到主activity
def check_ad_entry_activity(item, appEntryActivity, sdkEntryActivity):
    if sdkEntryActivity == None:
        return
    activityName = item.attrib["{%s}name" % Common.XML_NAMESPACE]
    if (activityName == sdkEntryActivity):
        element = ET.Element("meta-data")
        element.set("{%s}name" % Common.XML_NAMESPACE, "app_entry_name")
        element.set("{%s}value" % Common.XML_NAMESPACE, appEntryActivity)
        item.append(element)

#合并AndroidManifest.xml文件
def merge_manifest(decompiledfolder, sdkfolder):
    Log.out("[Logging...] 正在合并文件 : [AndroidManifest.xml]", True)
    if (os.path.exists(decompiledfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % decompiledfolder, True)
        return False
    if (os.path.exists(sdkfolder) == False):
        Log.out("[Logging...] 无法定位文件夹 %s" % sdkfolder, True)
        return False
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    sdkmanifest = "%s/AndroidManifest.xml" % sdkfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    gametree = ET.parse(manifestfile)
    gameroot = gametree.getroot()
    gameapplication = gameroot.find("application")

    sdktree = ET.parse(sdkmanifest)
    sdkroot = sdktree.getroot()
    sdkapplication = sdkroot.find("application")

    #处理入口Activity
    appEntryActivity, sdkEntryActivity = processEntryActivity(decompiledfolder, gameroot, sdkroot)

    for item in sdkroot.getchildren():
        if (item.tag == "uses-permission"):
            gameroot.append(item)

    for item in sdkapplication.getchildren():
        check_ad_entry_activity(item, appEntryActivity, sdkEntryActivity)
        gameapplication.append(item)

    Utils.indent(gameroot)
    gametree.write(manifestfile, encoding='utf-8', xml_declaration=True)
    Log.out("[Logging...] 文件合并完成\n", True)
    return True

#修改AndroidManifest.xml包名
def modify_package(decompiledfolder, pkg_suffix):
    if (pkg_suffix == None or pkg_suffix == ""):
        return
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    tree = ET.parse(manifestfile)
    root = tree.getroot()
    oldpkg = root.get("package")
    if (oldpkg != None and oldpkg != ""):
        newpkg = oldpkg + pkg_suffix
        Log.out("[Logging...] 修改配置包名 : [%s]" % newpkg, True)
        root.set("package", newpkg)
        Utils.indent(root)
        tree.write(manifestfile, encoding='utf-8', xml_declaration=True)

#添加meta到Application标签下面
def add_meta(decompiledfolder, meta_data):
    if (len(meta_data) <= 0):
        return
    manifestfile = "%s/AndroidManifest.xml" % decompiledfolder;
    ET.register_namespace('android', Common.XML_NAMESPACE)

    tree = ET.parse(manifestfile)
    root = tree.getroot()
    application = root.find("application")
    for data in meta_data:
        element = ET.Element("meta-data")
        name = Utils.getvalue(data, "name")
        value = Utils.getvalue(data, "value")
        element.set("{%s}name" % Common.XML_NAMESPACE, name)
        element.set("{%s}value" % Common.XML_NAMESPACE, value)
        application.append(element)
        Log.out("[Logging...] 添加元始数据 : [%s] --> [%s]" % (name, value), True)
    Utils.indent(root)
    tree.write(manifestfile, encoding='utf-8', xml_declaration=True)
    Log.out("[Logging...] 添加据据完成\n")
###############################################################################
if __name__ == "__main__":
    merge_manifest(r"D:\github\tools\packer\workspace\AbchDemo-ucsdk", r"D:\github\tools\packer\sdks\channels\ucsdk")