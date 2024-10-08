import getopt
import shutil
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

SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "base", "signapk.py")

def convert_bytes(byte_size):
    # 以可读的格式表示文件大小
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while byte_size >= 1024 and i < len(sizes) - 1:
        byte_size /= 1024.0
        i += 1
    return f"{byte_size:.2f} {sizes[i]}"

def get_file_size(file_path):
    # 获取文件大小
    if os.path.isfile(file_path):
        return os.path.getsize(file_path)
    else:
        return 0

def calc_file_size(file_path):
    file_size = get_file_size(file_path)
    return convert_bytes(file_size)

def recompiled_apk(apk_dir, apk_file):
    Log.out("[Logging...] {}".format("回编译文件中"))
    cmdlist = [Common.JAVA(), "-jar", Common.APKTOOL_JAR, 'b', apk_dir, '-o', apk_file]
    cmdlist += ["-s"]
    if not '-s' in cmdlist and not '--no-src' in cmdlist:
        cmdlist += ["--only-main-classes"]
    cmdlist += ["--use-aapt2"]
    cmdlist += ["--no-crunch"]
    showlist = []
    for cmd in cmdlist:
        showlist += [os.path.basename(cmd)]
    Log.out("[Logging...] 执行命令详情 : [%s]" % " ".join(showlist))
    ret = subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 回编文件完成")
    Log.out("")
    if (ret == 0) :
        return True
    else:
        return False

def decompiled_apk(apk_file, out_dir):
    Log.out("[Logging...] {}".format("反编译文件中"))
    cmdlist = [Common.JAVA(), "-jar", Common.APKTOOL_JAR, 'd', apk_file, '-o', out_dir]
    cmdlist += ["-s"]
    if not '-s' in cmdlist and not '--no-src' in cmdlist:
        cmdlist += ["--only-main-classes"]
    cmdlist += ["--use-aapt2"]
    showlist = []
    for cmd in cmdlist:
        showlist += [os.path.basename(cmd)]
    Log.out("[Logging...] 执行命令详情 : [%s]" % " ".join(showlist))
    ret = subprocess.call(cmdlist, stdout=subprocess.PIPE)
    Log.out("[Logging...] 编译文件完成")
    Log.out("")
    if (ret == 0) :
        return True
    else:
        return False

def extract_apks_to_dir(apks_file, apks_dir):
    Log.out("[Logging...] 解压安卓文件")
    all_apk_files = []
    with zipfile.ZipFile(apks_file, 'r') as apks_zip:
        for file_info in apks_zip.infolist():
            # 检查是否为APK文件
            if file_info.filename.endswith(".apk"):
                # 提取APK文件
                base_name = os.path.basename(file_info.filename)
                apk_filename = os.path.normpath(os.path.join(apks_dir, base_name))
                all_apk_files.append(apk_filename)
                if not os.path.exists(apk_filename):
                    apk_data = apks_zip.read(file_info.filename)
                    with open(apk_filename, 'wb') as apk_file:
                        apk_file.write(apk_data)
                    #print(f"Extracted {file_info.filename} to {apk_filename}")
    return all_apk_files

def apk2dir(apk_file):
    base_dir = os.path.dirname(apk_file)
    apk_name, ext = os.path.splitext(apk_file)
    return os.path.join(base_dir, apk_name)

def select_main_apk(all_apk_files):
    apk_file_size_result = []
    for item in all_apk_files:
        file_size = get_file_size(item)
        file_size_readable = convert_bytes(file_size)
        apk_file_size_result.append((item, file_size, file_size_readable))
    apk_file_size_result = sorted(apk_file_size_result, key=lambda item:-item[1])
    all_apk_files_sorted = []
    for item in apk_file_size_result:
        all_apk_files_sorted.append(apk2dir(item[0]))
    return all_apk_files_sorted[0], all_apk_files_sorted[1:]

def decompile_all_apk(all_apk_files):
    Log.out("[Logging...] 反编资源文件")
    for item in all_apk_files:
        decompiled_dir = apk2dir(item)
        #Log.out("[Logging...] decompiled_dir : {}".format(decompiled_dir))
        if not os.path.exists(decompiled_dir):
            decompiled_apk(item, decompiled_dir)
    pass

def merge_apk_resources(main_apk_dir, other_apks_dir):
    Log.out("[Logging...] 合并资源文件")
    for item in other_apks_dir:
        all_files = os.walk(item, True)
        for root, dirs, files in all_files:
            for file in files:
                srcfile = os.path.join(root, file)
                relative_dir = srcfile.replace(item, "")
                dstdir = root.replace(item, main_apk_dir)
                dstfile = os.path.join(dstdir, file)
                if not os.path.exists(dstfile) and (relative_dir.startswith("\lib") or relative_dir.startswith("/lib") or relative_dir.startswith("\\res") or relative_dir.startswith("/res")):
                    if not os.path.exists(dstdir):
                        os.makedirs(dstdir)
                    shutil.copy2(srcfile, dstfile)

def modify_axml_file(main_apk_dir):
    axml_file = os.path.join(main_apk_dir, "AndroidManifest.xml")
    ET.register_namespace('android', Common.XML_NAMESPACE)
    axml_tree = ET.parse(axml_file)
    axml_root = axml_tree.getroot()
    application = axml_root.find('application')
    extractNativeLibs = application.attrib.get("{%s}extractNativeLibs" % Common.XML_NAMESPACE)
    if extractNativeLibs == "false":
        application.attrib["{%s}extractNativeLibs" % Common.XML_NAMESPACE] = "true"
        axml_tree.write(axml_file, encoding='utf-8', xml_declaration=True)


def recompile_main_apk(main_apk_dir, final_main_apk):
    Log.out("[Logging...] 编译安卓文件 : {}".format(final_main_apk))
    recompiled_apk(main_apk_dir, final_main_apk)

def signapk(srcapk, dstapk):
    Log.out("[Logging...] 签名安卓文件")
    cmdlist = ["python", SIGNAPK_FILE, "-o", dstapk, srcapk]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        Log.out("[Logging...] 缺少参数: {} <apk>".format(os.path.basename(sys.argv[0])))
        sys.exit(0)

    apks_file = sys.argv[1]
    if apks_file == None or (not apks_file.endswith(".xapk") and not apks_file.endswith(".apks")):
        Log.out("[Logging...] {} 不是.apks或者.xpak文件")
        sys.exit(0)
    work_dir = os.path.dirname(apks_file)
    intermediates_dir = os.path.abspath(os.path.join(work_dir, 'intermediates'))
    if not os.path.exists(intermediates_dir):
        os.mkdir(intermediates_dir)
    apks_name, ext = os.path.splitext(os.path.basename(apks_file))
    apks_dir = os.path.realpath(os.path.join(intermediates_dir, apks_name))
    if not os.path.exists(apks_dir):
        os.mkdir(apks_dir)
    Log.out("[Logging...] 临时中间目录 : {} , ext : {}".format(apks_dir, ext))
    all_apk_files = extract_apks_to_dir(apks_file, apks_dir)
    main_apk_dir, other_apks_dir = select_main_apk(all_apk_files)
    Log.out("[Logging...] 主要文件目录 : {}\n".format(main_apk_dir))
    decompile_all_apk(all_apk_files)
    merge_apk_resources(main_apk_dir, other_apks_dir)

    recompile_apk_file = os.path.join(intermediates_dir, apks_name + "-unsigned.apk")
    final_apk_file = os.path.join(work_dir, apks_name + "-final.apk")
    modify_axml_file(main_apk_dir)
    if os.path.exists(final_apk_file):
        Utils.deleteFile(final_apk_file)

    recompile_main_apk(main_apk_dir, recompile_apk_file)

    signapk(recompile_apk_file, final_apk_file)

    Utils.deleteFile(recompile_apk_file)
    Log.out("[Logging...] 清除临时文件 : {}".format(apks_dir))
    Utils.deletedir(apks_dir)
    if intermediates_dir != None and os.path.exists(intermediates_dir):
        dir_size = len(os.listdir(intermediates_dir))
        Log.out("[Logging...] 临时目录大小 : {}".format(dir_size))
        if (dir_size <= 0):
            Log.out("[Logging...] 清除临时目录 : {}".format(intermediates_dir))
            Utils.deletedir(intermediates_dir)