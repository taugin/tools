#!/usr/bin/python
# coding: UTF-8

'''
合成渠道角标
'''
import _config
import Common
import Log
import Utils
import xml.etree.ElementTree as ET
import os
from PIL import Image
import glob

def find_corner_files(sdk_channel, cornerpos):
    '''搜索角标文件'''
    searchPath = os.path.join(sdk_channel, "corners", "%s*" % cornerpos)
    return glob.glob(searchPath)

def find_icon_files(decompiledfolder, icon_name):
    '''搜索应用图标文件'''
    searchPath = os.path.join(decompiledfolder, "res", "**", "%s.*" % icon_name)
    return glob.glob(searchPath)

def parse_icon_name(iconNode):
    '''解析图标文件'''
    if (iconNode != None):
        return iconNode.split("/")[1]
    return None

def find_apk_icon(decompiledfolder):
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
        return parse_icon_name(iconNode)

    iconNode = applicationNode.get("{%s}logo" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parse_icon_name(iconNode)

    mainactivity = manifestroot.findall(Common.MAIN_ACTIVITY_XPATH)
    if (mainactivity == None or len(mainactivity) <= 0):
        return None

    iconNode = mainactivity[0].get("{%s}icon" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parse_icon_name(iconNode)

    iconNode = mainactivity[0].get("{%s}logo" % Common.XML_NAMESPACE)
    if iconNode != None:
        return parse_icon_name(iconNode)

    return None

def add_corner_icon(iconfile, cornerfile):
    '''添加渠道角标'''
    icon_image = Image.open(iconfile)
    icon_w, icon_h = icon_image.size

    corner_image = Image.open(cornerfile)
    corner_w, corner_h = corner_image.size

    offset_w = icon_w - corner_w
    offset_h = icon_h - corner_h
    if False and (offset_w < 0 or offset_h < 0):
        Log.out("[Logging...] 无法合成角标 : offsetx : %d, offsety : %d" % (offset_w, offset_h))
        return
    icon_image.paste(corner_image, (offset_w, offset_h), corner_image)
    icon_image.save(iconfile, "png")
    icon_image.close()
    corner_image.close()

def find_proper_corner(icon_file, corner_files):
    '''找出合适的角标文件'''
    icon_image = Image.open(icon_file)
    (icon_w, icon_h) = icon_image.size
    icon_image.close()
    min_offsetw = icon_w
    min_offseth = icon_h
    proper_corner = None
    for corner_file in corner_files:
        corner_image = Image.open(corner_file)
        (corner_w, corner_h) = corner_image.size
        corner_image.close()
        #print("icon_w : %d, icon_h : %d, corner_w : %d, corner_h : %d" % (icon_w, icon_h, corner_w, corner_h))
        #从所有角标中寻找合适的角标
        if (True or corner_w <= icon_w and corner_h <= icon_h):
            offsetw = icon_w - corner_w
            offseth = icon_h - corner_h
            proper_corner = corner_file
            if abs(min_offsetw) > abs(offsetw) and abs(min_offseth) > abs(offseth):
                min_offsetw = offsetw
                min_offseth = offseth
                proper_corner = corner_file
    return proper_corner

def process_corner_icon(decompiledfolder, sdk_channel, cornerpos):
    '''进行角标处理'''
    icon_name = find_apk_icon(decompiledfolder)
    if (icon_name == None):
        Log.out("[Logging...] 没有找到图标\n")
        return
    if (cornerpos == None or len(cornerpos) <= 0):
        Log.out("[Logging...] 缺少角标位置\n")
        return

    icon_files = find_icon_files(decompiledfolder, icon_name)
    corner_files = find_corner_files(sdk_channel, cornerpos)
    if (corner_files == None or len(corner_files) <= 0):
        Log.out("[Logging...] 没有找到角标\n")
        return

    Log.out("[Logging...] 开始合成角标")
    for icon_file in icon_files:
        corner_file = find_proper_corner(icon_file, corner_files)
        if (corner_file != None):
            add_corner_icon(icon_file, corner_file)

    Log.out("[Logging...] 合成角标结束\n")

if __name__ == "__main__":
    #add_corner_icon(r"E:\temp\icon.png", r"E:\Github\tools\packer\sdks\channels\ucsdk\corners\rb_72x72.png")
    process_corner_icon(r"E:\Github\tools\packer\workspace\com.ninemgames.tennis.china-shly-shlysdk",
                         r"E:\Github\tools\packer\sdks\channels\ucsdk", "rb")
