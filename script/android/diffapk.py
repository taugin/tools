import subprocess
import sys
import os
import re
from time import sleep
import zipfile
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)
import Common
import Log
import Utils
import xml.etree.ElementTree as ET

def decompiled_apk(apk_file, out_dir):
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, 'd', apk_file, '-o', out_dir]
    cmdlist += ["--only-main-classes"]
    cmdlist += ["--use-aapt2"]
    ret = subprocess.call(cmdlist)
    Log.out("[Logging...] 编译完成")
    if (ret == 0) :
        return True
    else:
        return False

def compare_manifest_element(left_root, right_root, tag):
    '''对比活动'''
    left_apk_set = set()
    right_apk_set = set()
    left_apk_map = {}
    right_apk_map = {}
    for elem in left_root.iter():
        if elem.tag == tag:
            attrib = elem.attrib["{%s}name" % Common.XML_NAMESPACE]
            left_apk_set.add(attrib)
            left_apk_map[attrib] = elem

    for elem in right_root.iter():
        if elem.tag == tag:
            attrib = elem.attrib["{%s}name" % Common.XML_NAMESPACE]
            right_apk_set.add(attrib)
            right_apk_map[attrib] = elem
        
    added_apk_set = right_apk_set - left_apk_set
    removed_apk_set = left_apk_set - right_apk_set
    if len(added_apk_set) > 0 or len(removed_apk_set) > 0:
        readable_compare_name = None
        if tag == "uses-permission":
            readable_compare_name = "权限对比结果"
        elif tag == "permission":
            readable_compare_name = "自定义权限对比结果"
        elif tag == "activity":
            readable_compare_name = "活动对比结果"
        elif tag == "service":
            readable_compare_name = "服务对比结果"
        elif tag == "receiver":
            readable_compare_name = "广播对比结果"
        elif tag == "provider":
            readable_compare_name = "提供者对比结果"
        elif tag == "meta-data":
            readable_compare_name = "元数据对比结果"
        Log.out("[Logging...] {}{}".format(readable_compare_name, "+++++++++++++++++++++++++"))
        if len(added_apk_set) > 0:
            Log.out("[Logging...] {}".format("增加的条目"))
            for item in added_apk_set:
                desc = ET.tostring(right_apk_map.get(item), encoding='unicode')
                desc = ""
                Log.out("[Logging...] {} : {}".format(tag, item, desc))
        if len(removed_apk_set) > 0:
            Log.out("[Logging...] {}".format("减少的条目"))
            for item in removed_apk_set:
                desc = ET.tostring(left_apk_map.get(item), encoding='unicode')
                desc = ""
                Log.out("[Logging...] {} : {}".format(tag, item, desc))
        Log.out("")

def compare_manifest(decompiled_dir_left, decompiled_dir_right):
    '''对比AndroidManifest的变化'''
    manifest_left_file = os.path.join(decompiled_dir_left, "AndroidManifest.xml")
    manifest_right_file = os.path.join(decompiled_dir_right, "AndroidManifest.xml")
    #Log.out("[Logging...] 临时中间文件 : [{}, {}]".format(manifest_left_file, manifest_right_file))
    manifest_left_et = ET.parse(manifest_left_file)
    manifest_right_et = ET.parse(manifest_right_file)
    left_root = manifest_left_et.getroot()
    right_root = manifest_right_et.getroot()
    compare_manifest_element(left_root, right_root, "uses-permission")
    compare_manifest_element(left_root, right_root, "permission")
    compare_manifest_element(left_root, right_root, "activity")
    compare_manifest_element(left_root, right_root, "service")
    compare_manifest_element(left_root, right_root, "receiver")
    compare_manifest_element(left_root, right_root, "provider")
    compare_manifest_element(left_root, right_root, "meta-data")

def compare_resources(decompiled_dir_left, decompiled_dir_right):
    '''对比字符串的变化'''
    string_left_file = os.path.join(decompiled_dir_left, "res", "values", "strings.xml")
    string_right_file = os.path.join(decompiled_dir_right, "res", "values", "strings.xml")
    #Log.out("[Logging...] 临时中间文件 : [{}, {}]".format(string_left_file, string_right_file))
    string_left_et = ET.parse(string_left_file)
    string_right_et = ET.parse(string_right_file)
    left_root = string_left_et.getroot()
    right_root = string_right_et.getroot()
    left_apk_set = set()
    right_apk_set = set()
    left_apk_map = {}
    right_apk_map = {}
    for elem in left_root.iter():
        if elem.tag == "string":
            attrib = elem.text
            left_apk_map[attrib] = elem.attrib['name']
            left_apk_set.add(attrib)

    for elem in right_root.iter():
        if elem.tag == "string":
            attrib = elem.text
            right_apk_map[attrib] = elem.attrib['name']
            right_apk_set.add(attrib)
    added_apk_set = right_apk_set - left_apk_set
    removed_apk_set = left_apk_set - right_apk_set
    if len(added_apk_set) > 0 or len(removed_apk_set) > 0:
        Log.out("[Logging...] {}".format("字符串对比结果+++++++++++++++++++++++++"))
        Log.out("[Logging...] {}".format("增加的条目"))
        for item in added_apk_set:
            Log.out("[Logging...] {} -> {}".format(right_apk_map.get(item), item))
        Log.out("[Logging...] {}".format("减少的条目"))
        for item in removed_apk_set:
            Log.out("[Logging...] {} -> {}".format(left_apk_map.get(item), item))
        Log.out("")

def diff_apk(apk_left, apk_right):
    work_dir = os.path.dirname(apk_left)
    intermediates_dir = os.path.join(work_dir, 'intermediates')
    apk_left_name, ext = os.path.splitext(os.path.basename(apk_left))
    apk_right_name, ext = os.path.splitext(os.path.basename(apk_right))
    intermediates_left_dir = os.path.join(intermediates_dir, apk_left_name)
    intermediates_right_dir = os.path.join(intermediates_dir, apk_right_name)
    #Log.out("[Logging...] 临时中间目录 : [{}, {}]".format(intermediates_left_dir, intermediates_right_dir))
    if not os.path.exists(intermediates_left_dir):
        decompiled_apk(apk_left, intermediates_left_dir)
    if not os.path.exists(intermediates_right_dir):
        decompiled_apk(apk_right, intermediates_right_dir)
    compare_manifest(intermediates_left_dir, intermediates_right_dir)
    compare_resources(intermediates_left_dir, intermediates_right_dir)



if __name__ == "__main__":
    apk1_path = r"F:\workdir\decompile_analytics\TurboClean\3.7.1\TurboClean_3.7.1_Apkpure.apk"
    apk2_path = r"F:\workdir\decompile_analytics\TurboClean\3.7.2\TurboClean_3.7.2_Apkpure.apk"
    diff_apk(apk1_path, apk2_path)