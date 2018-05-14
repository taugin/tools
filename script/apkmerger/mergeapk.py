#!/usr/bin/python
# coding: UTF-8

import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Log
import shutil
import getopt
import Utils

import merge_builder
import merge_rfile
import merge_public
import merge_res
import merge_axml
import merge_apkfile
import merge_custom
import merge_smali

TRY_CONFIG = "error.json"
ONLY_CHECK_DUP = False
MERGE_BY_CONFIG = False

def fun_apk_decompile(apkfile, apkfolder):
    merge_builder.apk_decompile(apkfile, apkfolder)

def fun_apk_compile(masterfolder, mastermergedapk):
    merge_builder.apk_compile(masterfolder, mastermergedapk)

def fun_check_resdup(masterfolder, slavefolder):
    merge_rfile.check_resdup(masterfolder, slavefolder)

def fun_merge_xml_change_pkg(masterfolder, slavefolder, newpkgname):
    merge_axml.merge_xml_change_pkg(masterfolder, slavefolder, newpkgname)

def fun_rebuild_ids(masterfolder, slavefolder):
    merge_public.rebuild_ids(masterfolder, slavefolder)

def fun_merge_res(masterfolder, slavefolder):
    merge_res.merge_res(masterfolder, slavefolder)

def fun_merge_smali(masterfolder, slavefolder):
    merge_smali.merge_smali(masterfolder, slavefolder)

def fun_update_all_rfile(masterfolder):
    merge_rfile.update_all_rfile(masterfolder)

def fun_merge_custom(masterfolder, slavefolder):
    merge_custom.merge_custom(masterfolder, slavefolder)

def fun_clear_dup_smali(masterfolder):
    merge_smali.clear_dup_smali(masterfolder)

def fun_merge_apkfile(mastermergedapk, masterapk, slaveapk, company):
    merge_apkfile.merge_apkfile(mastermergedapk, masterapk, slaveapk, company)

def fun_signapk(mastermergedapk, mastersignedapk):
    merge_builder.signapk(mastermergedapk, mastersignedapk)

def fun_alignapk(mastersignedapk, masterfinalapk):
    merge_builder.alignapk(mastersignedapk, masterfinalapk)

###############################################################
def clean_tmp_folders(masterfolder, slavefolder, file1, file2):
    Log.out("[Logging...] 清除临时文件")
    try:
        #shutil.rmtree(masterfolder, ignore_errors = True)
        shutil.rmtree(slavefolder, ignore_errors = True)
        Utils.deleteFile(file1)
        Utils.deleteFile(file2)
    except:
        pass
    Log.out("[Logging...] 文件清除完成\n")

def mergeapk_batch(masterapk, slaveapk, output, newpkgname, company):
    (mastername, ext) = os.path.splitext(masterapk)
    masterfolder = mastername

    (slavename, ext) = os.path.splitext(slaveapk)
    slavefolder = slavename

    #生成合并后的apk名称
    tmpapk = masterapk
    if (output != None and output != ""):
        tmpapk = output

    (tmpname, ext) = os.path.splitext(tmpapk)
    mastermergedapk = tmpname + "-merged.apk"
    mastersignedapk = tmpname + "-merged-signed.apk"
    masterfinalapk = tmpname + "-merged-final.apk"

    if (newpkgname != None and newpkgname != ""):
        mastermergedapk = tmpname + "-" + newpkgname + "-merged.apk"
        mastersignedapk = tmpname + "-" + newpkgname + "-merged-signed.apk"
        masterfinalapk = tmpname + "-" + newpkgname + "-merged-final.apk"

    functions = []
    functions += [{"function":"fun_apk_decompile(masterapk, masterfolder)"}]
    functions += [{"function":"fun_apk_decompile(slaveapk, slavefolder)"}]
    functions += [{"function":"fun_check_resdup(masterfolder, slavefolder)"}]

    if (ONLY_CHECK_DUP == False):
        functions += [{"function":"fun_merge_xml_change_pkg(masterfolder, slavefolder, newpkgname)"}]
        functions += [{"function":"fun_rebuild_ids(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_merge_res(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_merge_smali(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_update_all_rfile(masterfolder)"}]
        functions += [{"function":"fun_merge_custom(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_clear_dup_smali(masterfolder)"}]
        functions += [{"function":"fun_apk_compile(masterfolder, mastermergedapk)", "saveonfalse":"True"}]
        functions += [{"function":"fun_merge_apkfile(mastermergedapk, masterapk, slaveapk, company)"}]
        functions += [{"function":"fun_signapk(mastermergedapk, mastersignedapk)"}]
        functions += [{"function":"fun_alignapk(mastersignedapk, masterfinalapk)"}]

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
        if (filename != None and filename == os.path.abspath(mastermergedapk)):
            pass
        func_exec_pos = saveflag["position"]
        os.remove(TRY_CONFIG)

    SAVE_ON_FALSE = False
    for item in range(0, length):
        if (item >= func_exec_pos):
            Log.out("--------------------------------------------")
            saveonfalse = False
            try:
                saveonfalse = eval(functions[item]["saveonfalse"])
            except:
                pass
            SAVE_ON_FALSE = saveonfalse
            Log.out("[Logging...] 当前函数编号 : [%.2d] [%s]" % (item + 1, functions[item]["function"].split("(")[0]))
            result = eval(functions[item]["function"])
            if (result == False):
                if (saveonfalse == True):
                    savestr = '{"position":%d,"filename":r"%s"}' % (item, os.path.abspath(mastermergedapk))
                    fd = open(TRY_CONFIG, "w")
                    fd.write(savestr)
                    fd.close()
                break
    if (SAVE_ON_FALSE == False):
        Log.out("--------------------------------------------")
        clean_tmp_folders(masterfolder, slavefolder, mastermergedapk, mastersignedapk)

def merge_according_cmdline(args):
    if (len(args) < 2):
        Log.out("[Logging...] 缺少参数: %s [-c] apk1 apk2" % os.path.basename(sys.argv[0]), True);
        sys.exit()
    masterapk = os.path.abspath(args[0])
    slaveapk = os.path.abspath(args[1])
    mergeapk_batch(masterapk, slaveapk, None, None, None)

#############################################################################
if (__name__ == "__main__"):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c")
        for op, value in opts:
            if (op == "-c"):
                ONLY_CHECK_DUP = True
    except getopt.GetoptError as err:
        Log.out(err)
        sys.exit()

    merge_according_cmdline(args)