#!/usr/bin/python
# coding: UTF-8

import os
import sys
import platform
import subprocess
import msvcrt

import decompile_apk
import compile_apk
import check_dup
import rebuild_ids
import copy_res
import merge_xml
import copy_fromapk

TRY_CONFIG = "mergeapk.tryagain"
SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "signtool", "signapk.py")

def log(str, show=True):
    if (show):
        print(str)

gameapk = os.path.abspath(sys.argv[1])
payapk = os.path.abspath(sys.argv[2])

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

functions = []
functions += ["decompile_apk.apk_decompile(gameapk, gamefolder)"]
functions += ["decompile_apk.apk_decompile(payapk, payfolder)"]
functions += ["check_dup.check_dup(gamefolder, payfolder)"]
functions += ["rebuild_ids.rebuild_ids(gamefolder, payfolder)"]
functions += ["copy_res.copy_res(gamefolder, payfolder)"]
functions += ["merge_xml.merge_xml(gamefolder, payfolder)"]
functions += ["compile_apk.apk_compile(gamefolder, gamemergedapk)"]
functions += ["copy_fromapk.copy_fromapk(gamemergedapk, gameapk, payapk)"]

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
        if (result == False):
            savestr = '{"function_pos":%d,"filename":r"%s"}' % (item, os.path.abspath(gamemergedapk))
            fd = open(TRY_CONFIG, "w")
            fd.write(savestr)
            fd.close()
            break