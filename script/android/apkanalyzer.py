import getopt
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

SEARCH_KEYWORDS_IN_CODE = False
COMPARE_APK_FILE = False

def decompiled_apk(apk_file, out_dir):
    Log.out("[Logging...] {}".format("反编译文件中"))
    cmdlist = [Common.JAVA, "-jar", Common.APKTOOL_JAR, 'd', apk_file, '-o', out_dir]
    if not SEARCH_KEYWORDS_IN_CODE:
        cmdlist += ["-s"]
    if not '-s' in cmdlist and not '--no-src' in cmdlist:
        cmdlist += ["--only-main-classes"]
    cmdlist += ["--use-aapt2"]
    showlist = []
    for cmd in cmdlist:
        showlist += [os.path.basename(cmd)]
    Log.out("[Logging...] 执行命令详情 : [%s]\n" % " ".join(showlist))
    ret = subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 编译完成")
    Log.out("")
    if (ret == 0) :
        return True
    else:
        return False

def analytics_ad_platform(decompiled_apk_dir):
    '''分析接入的广告平台'''
    script_file = os.path.normpath(sys.argv[0])
    script_dir = os.path.dirname(script_file)
    ad_info_file = os.path.join(script_dir, "ad_info.json")
    Log.out("[Logging...] 配置文件路径 : {}".format(ad_info_file))
    ad_info_json = None
    with open(ad_info_file, "r", encoding="utf-8") as f:
        ad_info_json = eval(f.read())
    #Log.out("ad_info_json : {}".format(ad_info_json))

    ad_platform_set = set()
    manifest_file = os.path.join(decompiled_apk_dir, "AndroidManifest.xml")
    manifest_et = ET.parse(manifest_file)
    root = manifest_et.getroot()
    for elem in root.iter():
        if elem.tag == "activity":
            element_name = elem.attrib["{%s}name" % Common.XML_NAMESPACE]
            for jitem in ad_info_json:
                platform = jitem.get('ad_platform')
                ad_prefix = jitem.get('ad_prefix')
                if ad_prefix != None and len(ad_prefix) > 0:
                    for prefix in ad_prefix:
                        if element_name.startswith(prefix):
                            ad_platform_set.add(platform)
    if ad_platform_set != None and len(ad_platform_set) > 0:
        Log.out("[Logging...] 已接广告平台 : {}".format(ad_platform_set))

def analyze_self_active(decompiled_apk_dir):
    '''分析自激活'''
    contains_self_active = False
    manifest_file = os.path.join(decompiled_apk_dir, "AndroidManifest.xml")
    manifest_et = ET.parse(manifest_file)
    root = manifest_et.getroot()
    for elem in root.iter():
        if elem.tag == 'provider':
            sync_value = elem.attrib.get("{%s}syncable" % Common.XML_NAMESPACE)
            if sync_value == 'true':
                meta_data = elem.find("meta-data")
                if meta_data != None:
                    meta_name = meta_data.attrib.get("{%s}name" % Common.XML_NAMESPACE)
                    meta_value = meta_data.attrib.get("{%s}value" % Common.XML_NAMESPACE)
                    if meta_name == 'android.content.ContactDirectory' and meta_value == 'true':
                        contains_self_active = True
                        break
    Log.out("[Logging...] 是否有自激活 : {}".format("有" if contains_self_active else "无"))

def analyze_instrumentation(decompiled_apk_dir):
    '''分析是否包含instrumentation, 疑似保活'''
    manifest_file = os.path.join(decompiled_apk_dir, "AndroidManifest.xml")
    manifest_et = ET.parse(manifest_file)
    root = manifest_et.getroot()
    ins_name = None
    for elem in root.iter():
        if elem.tag == 'instrumentation':
            ins_name = elem.attrib.get("{%s}name" % Common.XML_NAMESPACE)
    output = "有 : {}".format(ins_name) if ins_name != None else "无"
    Log.out("[Logging...] 有无保活组件 : {}".format(output))

def analyze_fullscreen_intent(decompiled_apk_dir):
    '''分析是否包含instrumentation, 疑似保活'''
    manifest_file = os.path.join(decompiled_apk_dir, "AndroidManifest.xml")
    manifest_et = ET.parse(manifest_file)
    root = manifest_et.getroot()
    has_fullscreen_intent = None
    for elem in root.iter():
        if elem.tag == 'uses-permission':
            permission = elem.attrib.get("{%s}name" % Common.XML_NAMESPACE)
            has_fullscreen_intent = permission == "android.permission.USE_FULL_SCREEN_INTENT"
            if has_fullscreen_intent:
                break
    output = "有" if has_fullscreen_intent else "无"
    Log.out("[Logging...] 全屏通知权限 : {}".format(output))

def analyze_account_sync(decompiled_apk_dir):
    '''分析是否包含instrumentation, 疑似保活'''
    manifest_file = os.path.join(decompiled_apk_dir, "AndroidManifest.xml")
    manifest_et = ET.parse(manifest_file)
    root = manifest_et.getroot()
    sync_adapter = root.find(".//service/meta-data[@{%s}name='android.content.SyncAdapter']" % Common.XML_NAMESPACE)
    account_authenticator = root.find(".//service/meta-data[@{%s}name='android.accounts.AccountAuthenticator']" % Common.XML_NAMESPACE)
    has_account_sync = (sync_adapter != None) and (account_authenticator != None)
    output = "有" if has_account_sync else "无"
    Log.out("[Logging...] 有无账户同步 : {}".format(output))


def analize_keywords(decompiled_apk_dir):
    keywords = ["makePathElements", "makeDexElements", "pathList", "dexElements", "createVirtualDisplay"]
    Log.out("\n[Logging...] 关键字段搜索+++++++++++++++++++++++++")
    Log.out("[Logging...] 关键字搜索中 : {}".format(keywords))
    smalidirs = ["smali", "smali_classes2", "smali_classes3", "smali_classes4", "smali_classes5", "smali_classes6", "smali_classes7", "smali_classes8", "smali_classes9", "smali_classes10"]
    search_result_set = set()
    for item in smalidirs:
        smali_dir = os.path.join(decompiled_apk_dir, item)
        if os.path.exists(smali_dir):
            mylist = os.walk(smali_dir, True)
            for root, filedir, files in mylist:
                for file in files:
                    relative_file = os.path.join(root, file)
                    abs_file = os.path.abspath(relative_file)
                    if os.path.exists(abs_file):
                        with open(abs_file, "r") as f:
                            content = f.read()
                            for word in keywords:
                                if word in content:
                                    search_result_set.add("{}#{}".format(word, relative_file))
    Log.out("[Logging...] 搜索关键结果 :")
    if search_result_set != None and len(search_result_set) > 0:
        for item in search_result_set:
            item_array = item.split("#")
            Log.out("[Logging...] {} : {}".format(item_array[0], item_array[1]))

def compare_manifest_element(old_root, new_root, tag):
    '''对比活动'''
    old_apk_set = set()
    new_apk_set = set()
    old_apk_map = {}
    new_apk_map = {}
    for elem in old_root.iter():
        if elem.tag == tag:
            attrib = elem.attrib["{%s}name" % Common.XML_NAMESPACE]
            old_apk_set.add(attrib)
            old_apk_map[attrib] = elem

    for elem in new_root.iter():
        if elem.tag == tag:
            attrib = elem.attrib["{%s}name" % Common.XML_NAMESPACE]
            new_apk_set.add(attrib)
            new_apk_map[attrib] = elem
        
    added_apk_set = new_apk_set - old_apk_set
    removed_apk_set = old_apk_set - new_apk_set
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
                desc = ET.tostring(new_apk_map.get(item), encoding='unicode')
                desc = ""
                Log.out("[Logging...] {} : {}".format(tag, item, desc))
        if len(removed_apk_set) > 0:
            Log.out("[Logging...] {}".format("减少的条目"))
            for item in removed_apk_set:
                desc = ET.tostring(old_apk_map.get(item), encoding='unicode')
                desc = ""
                Log.out("[Logging...] {} : {}".format(tag, item, desc))
        Log.out("")

def compare_manifest(decompiled_dir_old, decompiled_dir_new):
    '''对比AndroidManifest的变化'''
    manifest_old_file = os.path.join(decompiled_dir_old, "AndroidManifest.xml")
    manifest_new_file = os.path.join(decompiled_dir_new, "AndroidManifest.xml")
    #Log.out("[Logging...] 临时中间文件 : [{}, {}]".format(manifest_old_file, manifest_new_file))
    manifest_old_et = ET.parse(manifest_old_file)
    manifest_new_et = ET.parse(manifest_new_file)
    old_root = manifest_old_et.getroot()
    new_root = manifest_new_et.getroot()
    compare_manifest_element(old_root, new_root, "uses-permission")
    compare_manifest_element(old_root, new_root, "permission")
    compare_manifest_element(old_root, new_root, "activity")
    compare_manifest_element(old_root, new_root, "service")
    compare_manifest_element(old_root, new_root, "receiver")
    compare_manifest_element(old_root, new_root, "provider")
    compare_manifest_element(old_root, new_root, "meta-data")

def compare_string(decompiled_dir_old, decompiled_dir_new):
    '''对比字符串的变化'''
    string_old_file = os.path.join(decompiled_dir_old, "res", "values", "strings.xml")
    string_new_file = os.path.join(decompiled_dir_new, "res", "values", "strings.xml")
    string_old_et = ET.parse(string_old_file)
    string_new_et = ET.parse(string_new_file)
    old_root = string_old_et.getroot()
    new_root = string_new_et.getroot()
    old_apk_set = set()
    new_apk_set = set()
    old_apk_map = {}
    new_apk_map = {}
    for elem in old_root.iter():
        if elem.tag == "string":
            attrib = elem.text
            old_apk_map[attrib] = elem.attrib['name']
            old_apk_set.add(attrib)

    for elem in new_root.iter():
        if elem.tag == "string":
            attrib = elem.text
            new_apk_map[attrib] = elem.attrib['name']
            new_apk_set.add(attrib)
    added_apk_set = new_apk_set - old_apk_set
    removed_apk_set = old_apk_set - new_apk_set
    if len(added_apk_set) > 0 or len(removed_apk_set) > 0:
        Log.out("[Logging...] {}".format("资源对比结果+++++++++++++++++++++++++"))
        Log.out("[Logging...] {}".format("增加的条目"))
        for item in added_apk_set:
            Log.out("[Logging...] {} -> {}".format(new_apk_map.get(item), item))
        Log.out("[Logging...] {}".format("减少的条目"))
        for item in removed_apk_set:
            Log.out("[Logging...] {} -> {}".format(old_apk_map.get(item), item))
        Log.out("")

def compare_public(decompiled_dir_old, decompiled_dir_new):
    '''对比字符串的变化'''
    string_old_file = os.path.join(decompiled_dir_old, "res", "values", "public.xml")
    string_new_file = os.path.join(decompiled_dir_new, "res", "values", "public.xml")
    string_old_et = ET.parse(string_old_file)
    string_new_et = ET.parse(string_new_file)
    old_root = string_old_et.getroot()
    new_root = string_new_et.getroot()
    old_apk_set = set()
    new_apk_set = set()
    for elem in old_root.iter():
        if elem.tag == "public":
            name = elem.get('name')
            type = elem.get('type')
            attrib = "{}#{}".format(type, name)
            old_apk_set.add(attrib)

    for elem in new_root.iter():
        if elem.tag == "public":
            name = elem.get('name')
            type = elem.get('type')
            attrib = "{}#{}".format(type, name)
            new_apk_set.add(attrib)
    added_apk_set = new_apk_set - old_apk_set
    removed_apk_set = old_apk_set - new_apk_set
    if len(added_apk_set) > 0 or len(removed_apk_set) > 0:
        Log.out("[Logging...] {}".format("资源对比结果+++++++++++++++++++++++++"))
        Log.out("[Logging...] {}".format("增加的条目"))
        for item in added_apk_set:
            item_array = item.split('#')
            Log.out("[Logging...] {} -> {}".format(item_array[0], item_array[1]))
        Log.out("\n[Logging...] {}".format("减少的条目"))
        for item in removed_apk_set:
            item_array = item.split('#')
            Log.out("[Logging...] {} -> {}".format(item_array[0], item_array[1]))
        Log.out("")

def decompile_input_apk(apk_old, apk_new):
    work_dir = os.path.dirname(apk_new)
    intermediates_dir = os.path.join(work_dir, 'intermediates')
    intermediates_old_dir = None
    intermediates_new_dir = None
    if apk_old != None and len(apk_old) > 0:
        apk_old_name, ext = os.path.splitext(os.path.basename(apk_old))
        intermediates_old_dir = os.path.join(intermediates_dir, apk_old_name)
        if not os.path.exists(intermediates_old_dir):
            decompiled_apk(apk_old, intermediates_old_dir)
    if apk_new != None and len(apk_new) > 0:
        apk_new_name, ext = os.path.splitext(os.path.basename(apk_new))
        intermediates_new_dir = os.path.join(intermediates_dir, apk_new_name)
        if not os.path.exists(intermediates_new_dir):
            decompiled_apk(apk_new, intermediates_new_dir)
    return intermediates_old_dir, intermediates_new_dir

def compare_apk(intermediates_old_dir, intermediates_new_dir):
    compare_manifest(intermediates_old_dir, intermediates_new_dir)
    compare_string(intermediates_old_dir, intermediates_new_dir)
    compare_public(intermediates_old_dir, intermediates_new_dir)

def analyze_apk(intermediates_dir, apk_file):
    Log.out("\n[Logging...] {}".format("安卓整体分析+++++++++++++++++++++++++"))
    Log.out("[Logging...] {}".format("安卓文件路径 : {}".format(os.path.realpath(apk_file))))
    analytics_ad_platform(intermediates_dir)
    analyze_self_active(intermediates_dir)
    analyze_instrumentation(intermediates_dir)
    analyze_fullscreen_intent(intermediates_dir)
    analyze_account_sync(intermediates_dir)
    if SEARCH_KEYWORDS_IN_CODE:
        analize_keywords(intermediates_dir)


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "sc")
        for op, value in opts:
            if (op == "-s"):
                SEARCH_KEYWORDS_IN_CODE = True
            elif (op == "-c"):
                COMPARE_APK_FILE = True
    except getopt.GetoptError as err:
        Log.out(err)
        sys.exit()

    if len(args) < 0:
        Log.out("[Logging...] 缺少apk参数: {} <apk>".format(os.path.basename(sys.argv[0])))
        sys.exit(0)

    intermediates_old_dir = None
    intermediates_new_dir = None
    if len(args) >=2 and COMPARE_APK_FILE:
        apk_old = args[0]
        apk_new = args[1]
        if not os.path.exists(apk_old):
            Log.out("[Logging...] apk文件不存在: {}".format(apk_old))
            sys.exit(0)
        if not os.path.exists(apk_new):
            Log.out("[Logging...] apk文件不存在: {}".format(apk_new))
            sys.exit(0)
        intermediates_old_dir, intermediates_new_dir = decompile_input_apk(apk_old, apk_new)
        compare_apk(intermediates_old_dir, intermediates_new_dir)
        analyze_apk(intermediates_new_dir, apk_new)
    else:
        for item in args:
            apk_file = item
            if os.path.exists(apk_file):
                intermediates_old_dir, intermediates_new_dir = decompile_input_apk(None, apk_file)
                analyze_apk(intermediates_new_dir, apk_file)