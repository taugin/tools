#!/usr/bin/python
# coding: UTF-8

import os
import sys
import platform
import subprocess
import msvcrt
import shutil
import getopt

import decompile_apk
import compile_apk
import check_dup
import rebuild_ids
import copy_res
import merge_xml
import copy_fromapk

TRY_CONFIG = "mergeapk.tryagain"
SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "signtool", "signapk.py")
ONLY_CHECK_DUP = False

def log(str, show=True):
    if (show):
        print(str)

try:
    opts, args = getopt.getopt(sys.argv[1:], "c")
    for op, value in opts:
        if (op == "-c"):
            ONLY_CHECK_DUP = True
except getopt.GetoptError as err:
    log(err)
    sys.exit()

if (len(args) < 2):
    log("[Logging...] 缺少参数: %s [-c] apk1 apk2" % os.path.basename(sys.argv[0]), True);
    sys.exit()

gameapk = os.path.abspath(args[0])
payapk = os.path.abspath(args[1])

(name, ext) = os.path.splitext(gameapk)
gamefolder = name
gamemergedapk = name + "-merged.apk"
(name, ext) = os.path.splitext(payapk)
payfolder = name

def signapk_use_testkey(apkloaderfile):
    log("")
    cmdlist = ["python", SIGNAPK_FILE, "-t", apkloaderfile]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

def clean_tmp_folders(gamefolder, payfolder):
    log("[Logging...] 清除临时文件")
    shutil.rmtree(payfolder, ignore_errors = True)
    log("[Logging...] 临时文件清除完成")

functions = []
functions += ["decompile_apk.apk_decompile(gameapk, gamefolder)"]
functions += ["decompile_apk.apk_decompile(payapk, payfolder)"]
functions += ["check_dup.check_dup(gamefolder, payfolder)"]

if (ONLY_CHECK_DUP == False):
    functions += ["rebuild_ids.rebuild_ids(gamefolder, payfolder)"]
    functions += ["copy_res.copy_res(gamefolder, payfolder)"]
    functions += ["merge_xml.merge_xml(gamefolder, payfolder)"]
    functions += ["compile_apk.apk_compile(gamefolder, gamemergedapk)"]
    functions += ["copy_fromapk.copy_fromapk(gamemergedapk, gameapk, payapk)"]
    functions += ["clean_tmp_folders(gamefolder, payfolder)"]
    if (platform.system().lower() == "windows"):
        functions += ["signapk_use_testkey(gamemergedapk)"]

result = False
length = len(functions)
func_exec_pos = 0
if (os.path.exists(TRY_CONFIG)):
    f = open(TRY_CONFIG, "r");
    string = f.read()
    f.close()
    saveflag = eval(string)
    filename = saveflag["filename"]
    if (filename != None and filename == os.path.abspath(gamemergedapk)):
        func_exec_pos = saveflag["function_pos"]
    os.remove(TRY_CONFIG)

for item in range(0, length):
    if (item >= func_exec_pos):
        log("--------------------------------------------")
        result = eval(functions[item])
        if (result == False and ONLY_CHECK_DUP == False):
            savestr = '{"function_pos":%d,"filename":r"%s"}' % (item, os.path.abspath(gamemergedapk))
            fd = open(TRY_CONFIG, "w")
            fd.write(savestr)
            fd.close()
            break
if (ONLY_CHECK_DUP):
    log("--------------------------------------------")
    clean_tmp_folders(gamefolder, payfolder)

