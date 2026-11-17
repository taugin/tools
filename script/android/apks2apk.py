import getopt
import shutil
import subprocess
import sys
import os
import re
import unicodedata
from time import sleep, monotonic
import zipfile
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)
import PathCompat
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
    if os.path.isfile(PathCompat.fsPath(file_path)):
        return os.path.getsize(PathCompat.fsPath(file_path))
    else:
        return 0

def calc_file_size(file_path):
    file_size = get_file_size(file_path)
    return convert_bytes(file_size)

def recompiled_apk(apk_dir, apk_file):
    Log.out("[Logging...] {}".format("回编译文件中"))
    cmdlist = [Common.JAVA(), "-jar", Common.APKTOOL_JAR, 'b', apk_dir, '-o', apk_file]
    #cmdlist += ["-s"]
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
    cmdlist = [Common.JAVA(), "-jar", Common.APKTOOL_JAR, 'd', apk_file, '-o', out_dir, '--res-resolve-mode', 'lazy', '-q']
    # 需要反编译代码，供后续修改 Smali 调用。cmdlist += ["-s"]
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
    with zipfile.ZipFile(PathCompat.fsPath(apks_file), 'r') as apks_zip:
        for file_info in apks_zip.infolist():
            # 检查是否为APK文件
            if file_info.filename.endswith(".apk"):
                # 提取APK文件
                base_name = os.path.basename(file_info.filename)
                apk_filename = os.path.normpath(os.path.join(apks_dir, base_name))
                all_apk_files.append(apk_filename)
                if not os.path.exists(PathCompat.fsPath(apk_filename)):
                    apk_data = apks_zip.read(file_info.filename)
                    with open(PathCompat.fsPath(apk_filename), 'wb') as apk_file:
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
    Log.out(f"[Logging...] 反编资源文件 : [{len(all_apk_files)}]\n")
    for item in all_apk_files:
        decompiled_dir = apk2dir(item)
        #Log.out("[Logging...] decompiled_dir : {}".format(decompiled_dir))
        if not os.path.exists(PathCompat.fsPath(decompiled_dir)):
            decompiled_apk(item, decompiled_dir)
    pass

def merge_apk_resources(main_apk_dir, other_apks_dir):
    Log.out("[Logging...] 合并资源文件")
    for item in other_apks_dir:
        all_files = PathCompat.walk(item, True)
        for root, dirs, files in all_files:
            for file in files:
                srcfile = os.path.join(root, file)
                relative_dir = srcfile.replace(item, "")
                dstdir = root.replace(item, main_apk_dir)
                dstfile = os.path.join(dstdir, file)
                if not os.path.exists(PathCompat.fsPath(dstfile)) and (relative_dir.startswith("\lib") or relative_dir.startswith("/lib") or relative_dir.startswith("\\res") or relative_dir.startswith("/res")):
                    if not os.path.exists(PathCompat.fsPath(dstdir)):
                        os.makedirs(PathCompat.fsPath(dstdir))
                    shutil.copy2(PathCompat.fsPath(srcfile), PathCompat.fsPath(dstfile))
    Log.out("[Logging...] 合并文件完成\n")

def modify_axml_file(main_apk_dir):
    axml_file = os.path.join(main_apk_dir, "AndroidManifest.xml")
    ET.register_namespace('android', Common.XML_NAMESPACE)
    axml_tree = ET.parse(PathCompat.fsPath(axml_file))
    axml_root = axml_tree.getroot()

    # ---------- 删除 manifest 上的 split 属性 ----------
    for attr in ["isSplitRequired", "requiredSplitTypes", "splitTypes", "split"]:
        full_key = "{%s}%s" % (Common.XML_NAMESPACE, attr)
        if full_key in axml_root.attrib:
            value = axml_root.attrib.get("{%s}%s" % (Common.XML_NAMESPACE, attr), "")
            print(f"[Logging...] 删除资源属性 : [manifest]{attr} : {value}")
            del axml_root.attrib[full_key]

    # ---------- 删除 <uses-split> ----------
    for uses_split in axml_root.findall("uses-split"):
        axml_root.remove(uses_split)
        print(f"[Logging...] 删除资源属性 : {uses_split}")

    # ---------- 删除 <application> 下的 split 相关 meta-data ----------
    application = axml_root.find("application")
    if application is not None:
        # 修改 extractNativeLibs
        extractNativeLibs = application.attrib.get("{%s}extractNativeLibs" % Common.XML_NAMESPACE)
        if extractNativeLibs == "false":
            application.attrib["{%s}extractNativeLibs" % Common.XML_NAMESPACE] = "true"
            print(f"[Logging...] 修改资源属性 : [application]extractNativeLibs=[false -> true]")

        for provider in application.findall("provider"):
            name = provider.attrib.get("{%s}name" % Common.XML_NAMESPACE, "")
            if name == "com.pairip.licensecheck.LicenseContentProvider":
                provider.attrib["{%s}enabled" % Common.XML_NAMESPACE]="false"
                print(f"[Logging...] 删除资源属性 : [provider]name : {name}, enabled[true -> false]")

        # 删除 meta-data 里和 split 相关的
        for meta in application.findall("meta-data"):
            name = meta.attrib.get("{%s}name" % Common.XML_NAMESPACE, "")
            value = meta.attrib.get("{%s}value" % Common.XML_NAMESPACE, "")
            resource = meta.attrib.get("{%s}resource" % Common.XML_NAMESPACE, "")
            if name in ["com.android.vending.splits.required", "com.android.vending.splits", "com.android.vending.derived.apk.id", "com.android.stamp.source", "com.android.stamp.type"]:
                application.remove(meta)
                print(f"[Logging...] 删除资源属性 : [meta-data]name : {name}, value : {value}, resource : [{resource}]")
            elif value == "@null" or resource == "@null":
                application.remove(meta)
                print(f"[Logging...] 删除资源属性 : [meta-data]name : {name}, value : {value}, resource : [{resource}]")

    # ---------- 保存 ----------
    axml_tree.write(PathCompat.fsPath(axml_file), encoding="utf-8", xml_declaration=True)
    Log.out("")

def remove_check_licence(main_apk_dir):
    Log.out("[Logging...] 注释许可检查")
    started_at = monotonic()
    last_progress_at = started_at
    scanned_count = 0
    progress_visible = False
    progress_width = 0

    def update_progress(message):
        nonlocal progress_visible, progress_width
        # 覆盖同一行，并清除较长的上一条状态留下的字符。
        width = sum(2 if unicodedata.east_asian_width(char) in ("W", "F") else 1 for char in message)
        Log.out("\r" + message + " " * max(0, progress_width - width) + "\r", end="")
        progress_visible = True
        progress_width = width

    def finish_progress():
        nonlocal progress_visible, progress_width
        # 普通日志另起一行，避免覆盖进度或与进度拼接。
        if progress_visible:
            Log.out("")
            progress_visible = False
            progress_width = 0
    target_method = "Lcom/pairip/licensecheck/LicenseClient;->checkLicense(Landroid/content/Context;)V"
    call_pattern = re.compile(
        r"^(\s*)invoke-static(?:/range)?\s+\{[^}]*\},\s*"
        r"Lcom/pairip/licensecheck/LicenseClient;->checkLicense\(Landroid/content/Context;\)V"
        r"\s*(?:#.*)?$"
    )
    modified_count = 0
    for directory in os.listdir(PathCompat.fsPath(main_apk_dir)):
        smali_dir = os.path.join(main_apk_dir, directory)
        if not directory.startswith("smali") or not os.path.isdir(PathCompat.fsPath(smali_dir)):
            continue
        # 只显示目录名，避免完整路径过长导致终端自动折行。
        update_progress(f"[Logging...] 开始扫描文件 : [{directory}]")
        # 遍历失败必须暴露，避免跳过目录后仍显示处理完成。
        def on_walk_error(error):
            raise error
        for root, dirs, files in PathCompat.walk(smali_dir, onerror=on_walk_error):
            for filename in files:
                if not filename.endswith(".smali"):
                    continue
                file_path = os.path.join(root, filename)
                now = monotonic()
                if now - last_progress_at >= 2:
                    update_progress(f"[Logging...] 正在扫描文件 : 已扫描 {scanned_count} 个 Smali，已修改 {modified_count} 处，耗时 {now - started_at:.1f}s")
                    last_progress_at = now
                with open(PathCompat.fsPath(file_path), "r", encoding="utf-8", newline="") as smali_file:
                    content = smali_file.read()
                scanned_count += 1
                # 大多数文件无目标调用，先快速筛选，避免逐行创建对象和执行正则。
                if target_method not in content:
                    continue
                lines = content.splitlines(keepends=True)
                file_count = 0
                for index, line in enumerate(lines):
                    if target_method not in line:
                        continue
                    match = call_pattern.fullmatch(line.rstrip("\r\n"))
                    if match is not None:
                        # 保留缩进、原始指令和换行，已注释的调用不会重复处理。
                        indent = match.group(1)
                        lines[index] = indent + "# " + line[len(indent):]
                        file_count += 1
                if file_count:
                    with open(PathCompat.fsPath(file_path), "w", encoding="utf-8", newline="") as smali_file:
                        smali_file.writelines(lines)
                    modified_count += file_count
                    finish_progress()
                    Log.out(f"[Logging...] 注释许可调用 : [{file_path}] : {file_count}")
    finish_progress()
    Log.out(f"[Logging...] 注释调用次数 : {modified_count}，已扫描 {scanned_count} 个 Smali，耗时 {monotonic() - started_at:.1f}s\n")


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
        Log.out("[Logging...] 缺少参数 : {} <apk>".format(os.path.basename(sys.argv[0])))
        Log.out("[Logging...] 参数选项 : -p 编译前暂停，等待用户手动修改")
        sys.exit(0)
    paused_before_compile = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p")
        for op, value in opts:
            if (op == "-p"):
                paused_before_compile = True
    except getopt.GetoptError as err:
        Log.out(err)
        sys.exit()

    apks_file = args[0]

    if apks_file == None or (not apks_file.endswith(".xapk") and not apks_file.endswith(".apks")):
        Log.out("[Logging...] {} 不是.apks或者.xpak文件")
        sys.exit(0)
    work_dir = os.path.dirname(apks_file)
    intermediates_dir = os.path.abspath(os.path.join(work_dir, 'intermediates'))
    if not os.path.exists(PathCompat.fsPath(intermediates_dir)):
        os.mkdir(PathCompat.fsPath(intermediates_dir))
    apks_name, ext = os.path.splitext(os.path.basename(apks_file))
    apks_dir = os.path.realpath(os.path.join(intermediates_dir, apks_name))
    if not os.path.exists(PathCompat.fsPath(apks_dir)):
        os.mkdir(PathCompat.fsPath(apks_dir))
    Log.out("[Logging...] 临时中间目录 : {} , ext : {}".format(apks_dir, ext))
    all_apk_files = extract_apks_to_dir(apks_file, apks_dir)
    main_apk_dir, other_apks_dir = select_main_apk(all_apk_files)
    Log.out("[Logging...] 主要文件目录 : {}\n".format(main_apk_dir))
    decompile_all_apk(all_apk_files)
    merge_apk_resources(main_apk_dir, other_apks_dir)

    recompile_apk_file = os.path.join(intermediates_dir, apks_name + "-unsigned.apk")
    final_apk_file = os.path.join(work_dir, apks_name + "-final.apk")
    modify_axml_file(main_apk_dir)
    remove_check_licence(main_apk_dir)
    if os.path.exists(PathCompat.fsPath(final_apk_file)):
        Utils.deleteFile(final_apk_file)

    if paused_before_compile:
        Utils.pause("\n[Logging...] 临时暂停编译 : 手工修改资源文件\n")

    recompile_main_apk(main_apk_dir, recompile_apk_file)

    signapk(recompile_apk_file, final_apk_file)

    Utils.deleteFile(recompile_apk_file)
    Log.out("[Logging...] 清除临时文件 : {}".format(apks_dir))
    Utils.deletedir(apks_dir)
    if intermediates_dir != None and os.path.exists(PathCompat.fsPath(intermediates_dir)):
        dir_size = len(os.listdir(PathCompat.fsPath(intermediates_dir)))
        Log.out("[Logging...] 临时目录大小 : {}".format(dir_size))
        if (dir_size <= 0):
            Log.out("[Logging...] 清除临时目录 : {}".format(intermediates_dir))
            Utils.deletedir(intermediates_dir)
