#!/usr/bin/python
# coding: UTF-8

import os
import sys
import platform
import subprocess
import shutil
import getopt

import decompile_apk
import compile_apk
import check_dup
import rebuild_ids
import copy_res
import merge_xml
import copy_fromapk
import config_parser
import platform

TRY_CONFIG = "error.json"
SIGNAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "..", "signtool", "signapk.py")
ONLY_CHECK_DUP = False
MERGE_BY_CONFIG = False

def log(str, show=True):
    if (show):
        print(str)

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
    try:
        shutil.rmtree(gamefolder, ignore_errors = True)
        shutil.rmtree(payfolder, ignore_errors = True)
    except:
        pass
    log("[Logging...] 文件清除完成\n")

def mergeapk_batch(gameapk, payapk, output, newpkgname, company):
    (gamename, ext) = os.path.splitext(gameapk)
    gamefolder = gamename

    (payname, ext) = os.path.splitext(payapk)
    payfolder = payname

    #生成合并后的apk名称
    tmpapk = gameapk
    if (output != None and output != ""):
        tmpapk = output

    (tmpname, ext) = os.path.splitext(tmpapk)
    gamemergedapk = tmpname + "-merged.apk"

    if (newpkgname != None and newpkgname != ""):
        gamemergedapk = tmpname + "-" + newpkgname + "-merged.apk"

    functions = []
    functions += [{"function":"decompile_apk.apk_decompile(gameapk, gamefolder)"}]
    functions += [{"function":"decompile_apk.apk_decompile(payapk, payfolder)"}]
    functions += [{"function":"check_dup.check_dup(gamefolder, payfolder)"}]

    if (ONLY_CHECK_DUP == False):
        functions += [{"function":"merge_xml.merge_xml_change_pkg(gamefolder, payfolder, newpkgname)"}]
        functions += [{"function":"rebuild_ids.rebuild_ids(gamefolder, payfolder, company)"}]
        functions += [{"function":"copy_res.copy_res(gamefolder, payfolder)"}]
        functions += [{"function":"compile_apk.apk_compile(gamefolder, gamemergedapk)", "saveonfalse":"True"}]
        functions += [{"function":"copy_fromapk.copy_fromapk(gamemergedapk, gameapk, payapk, company)"}]
        functions += [{"function":"signapk_use_testkey(gamemergedapk)"}]

    result = False
    length = len(functions)
    func_exec_pos = 0
    if (os.path.exists(TRY_CONFIG)):
        f = open(TRY_CONFIG, "r");
        string = f.read()
        f.close()
        saveflag = eval(string)
        filename = None
        try:
            filename = saveflag["filename"]
        except:
            pass
        if (filename != None and filename == os.path.abspath(gamemergedapk)):
            pass
        func_exec_pos = saveflag["position"]
        os.remove(TRY_CONFIG)

    SAVE_ON_FALSE = False
    for item in range(0, length):
        if (item >= func_exec_pos):
            log("--------------------------------------------")
            saveonfalse = False
            try:
                saveonfalse = eval(functions[item]["saveonfalse"])
            except:
                pass
            SAVE_ON_FALSE = saveonfalse
            log("[Logging...] 当前函数编号 : [%d]" % item)
            result = eval(functions[item]["function"])
            if (result == False):
                if (saveonfalse == True):
                    savestr = '{"position":%d,"filename":r"%s"}' % (item, os.path.abspath(gamemergedapk))
                    fd = open(TRY_CONFIG, "w")
                    fd.write(savestr)
                    fd.close()
                break
    if (SAVE_ON_FALSE == False):
        log("--------------------------------------------")
        clean_tmp_folders(gamefolder, payfolder)

def merge_according_cmdline(args):
    if (len(args) < 2):
        log("[Logging...] 缺少参数: %s [-c] apk1 apk2" % os.path.basename(sys.argv[0]), True);
        sys.exit()
    gameapk = os.path.abspath(args[0])
    payapk = os.path.abspath(args[1])
    mergeapk_batch(gameapk, payapk, None, None, None)

def merge_according_config():
    list = config_parser.readmergelist()
    for item in list:
        gameapk = item.get("gameapk")
        payapk = item.get("payapk")
        output = item.get("output")
        package = item.get("package")
        company = item.get("company")
        if (gameapk != None and gameapk != "" and payapk != None and payapk != ""):
            log("[Logging...] ================================================")
            log("[Logging...] 游戏APK : [%s]" % gameapk)
            log("[Logging...] 支付APK : [%s]\n" % payapk)
            mergeapk_batch(gameapk, payapk, output, package, company)
        else:
            log("[Logging...] 请至少配置 <gameapk> 和 <payapk>项")

#############################################################################
if (__name__ == "__main__"):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cf")
        for op, value in opts:
            if (op == "-c"):
                ONLY_CHECK_DUP = True
            elif (op == "-f"):
                MERGE_BY_CONFIG = True
    except getopt.GetoptError as err:
        log(err)
        sys.exit()

    if (MERGE_BY_CONFIG):
        merge_according_config()
    else:
        merge_according_cmdline(args)