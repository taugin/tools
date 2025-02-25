#!/usr/bin/python
# coding: UTF-8

import sys
import os
import platform
import subprocess
import time
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Log
import shutil
import getopt
import Utils
import Common

import merge_builder
import merge_rfile
import merge_public
import merge_res
import merge_axml
import merge_apkfile
import merge_custom
import merge_smali

TRY_CONFIG = "error.json"
CHECK_DUP = False
DEBUG_MODE = False
NAME_TEMPLATE = None
FORMAT_LABEL = "{apklabel}"
FORMAT_VERNAME = "{vername}"
FORMAT_VERCODE = "{vercode}"
FORMAT_DATETIME = "{datetime}"


def task(task_name, fun, *args, **kwargs):
    Log.out("[Logging...] 当前函数名称 : [%s]" % task_name)
    start_time = time.time()
    fun(*args, **kwargs)
    end_time = time.time()
    Log.out("[Logging...] 功能运行耗时 : [%.2fs]" % (end_time - start_time))

def pause():
    if (platform.system().lower() == "windows"):
        import msvcrt
        Log.out("[Logging...] 操作完成，按任意键退出", True)
        msvcrt.getch()

def fun_apk_decompile(apkfile, apkfolder):
    ret = merge_builder.apk_decompile(apkfile, apkfolder)
    if ret == False:
        pause()
        sys.exit(0)

def fun_apk_compile(masterfolder, mastermergedapk):
    ret = merge_builder.apk_compile(masterfolder, mastermergedapk)
    if ret == False:
        pause()
        sys.exit(0)

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
    merge_rfile.update_all_rfile(masterfolder, DEBUG_MODE)

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
def get_app_info(apkFile):
    '''输出apk的包信息'''
    apk_info = {}
    cmdlist = [Common.AAPT2_BIN, "d", "badging", apkFile]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, shell=False)

    tmppkg = ""
    tmp = ""
    alllines = process.stdout.readlines()
    for line in alllines :
        tmp = Utils.parseString(line)
        if (tmp.startswith("package: ")  and "pkgname" not in apk_info):
            tmppkg = tmp[len("package: "):]
            tmppkg = tmppkg.replace("\r", "")
            tmppkg = tmppkg.replace("\n", "")
            tmppkg = tmppkg.replace("'", "")
            tmpsplit = tmppkg.split(" ")
            pkgname = None
            vercode = None
            vername = None
            if tmpsplit != None and len(tmpsplit) >= 3:
                pkgname = tmpsplit[0].split("=")[1]
                vercode = tmpsplit[1].split("=")[1]
                vername = tmpsplit[2].split("=")[1]
            apk_info["pkgname"] = pkgname
            apk_info["vercode"] = vercode
            apk_info["vername"] = vername
        elif (tmp.startswith("application-label") and "apklabel" not in apk_info):
            tmppkg = tmp
            tmppkg = tmppkg.replace("\r", "")
            tmppkg = tmppkg.replace("\n", "")
            tmppkg = tmppkg.replace("'", "")
            label = tmppkg.split(":")[1]
            apk_info["apklabel"] = label
    apk_info["datetime"] = time.strftime("%Y-%m-%d", time.localtime())
    return apk_info

def clean_tmp_folders(masterfolder, slavefolder, file1, file2):
    try:
        Log.out("[Logging...] 清除临时文件 : [%s]" % file1)
        Utils.deleteFile(file1)
        Log.out("[Logging...] 清除临时文件 : [%s]" % file2)
        Utils.deleteFile(file2)
        if (not DEBUG_MODE):
            Log.out("[Logging...] 清除临时文件 : [%s]" % masterfolder)
            shutil.rmtree(masterfolder, ignore_errors = True)
            Log.out("[Logging...] 清除临时文件 : [%s]" % slavefolder)
            shutil.rmtree(slavefolder, ignore_errors = True)
    except:
        pass
    Log.out("[Logging...] 文件清除完成\n")

def mergeapk_batch(masterapk, slaveapk, output, newpkgname, company):
    mastername = os.path.splitext(masterapk)
    masterfolder = mastername[0]

    slavename = os.path.splitext(slaveapk)
    slavefolder = slavename[0]

    #生成合并后的apk名称
    tmpapk = masterapk
    if (output != None and output != ""):
        tmpapk = output

    tmpname = os.path.splitext(tmpapk)
    mastermergedapk = tmpname[0] + "-merged.apk"
    mastersignedapk = tmpname[0] + "-merged-signed.apk"
    masterfinalapk = tmpname[0] + "-merged-final.apk"

    if (newpkgname != None and newpkgname != ""):
        mastermergedapk = tmpname + "-" + newpkgname + "-merged.apk"
        mastersignedapk = tmpname + "-" + newpkgname + "-merged-signed.apk"
        masterfinalapk = tmpname + "-" + newpkgname + "-merged-final.apk"

    functions = []
    functions += [{"function":"fun_apk_decompile(masterapk, masterfolder)"}]
    functions += [{"function":"fun_apk_decompile(slaveapk, slavefolder)"}]
    #functions += [{"function":"fun_check_resdup(masterfolder, slavefolder)"}]

    if (CHECK_DUP == False):
        functions += [{"function":"fun_merge_xml_change_pkg(masterfolder, slavefolder, newpkgname)"}]
        functions += [{"function":"fun_rebuild_ids(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_merge_res(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_merge_smali(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_merge_custom(masterfolder, slavefolder)"}]
        functions += [{"function":"fun_update_all_rfile(masterfolder)"}]
        functions += [{"function":"fun_clear_dup_smali(masterfolder)"}]
        functions += [{"function":"fun_apk_compile(masterfolder, mastermergedapk)", "saveonfalse":"True"}]
        functions += [{"function":"fun_merge_apkfile(mastermergedapk, masterapk, slaveapk, company)"}]
        functions += [{"function":"fun_signapk(mastermergedapk, mastersignedapk)"}]
        #functions += [{"function":"fun_alignapk(mastersignedapk, masterfinalapk)"}]

    has_align_fun = False
    for fun in functions:
        if (fun["function"].startswith("fun_alignapk")):
            has_align_fun = True
            break;
    Log.out("[Logging...] 允许文件对齐 : %s" % has_align_fun)

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
            start_time = time.time()
            result = eval(functions[item]["function"])
            end_time = time.time()
            Log.out("[Logging...] 功能运行耗时 : [%.2fs]" % (end_time - start_time))
            if (result == False):
                if (saveonfalse == True):
                    savestr = '{"position":%d,"filename":r"%s"}' % (item, os.path.abspath(mastermergedapk))
                    fd = open(TRY_CONFIG, "w")
                    fd.write(savestr)
                    fd.close()
                break
    #允许文件对齐的话，使用masterfinalapk，否则使用mastersignedapk
    rename_with_template(masterfinalapk if has_align_fun else mastersignedapk)
    if (SAVE_ON_FALSE == False):
        Log.out("--------------------------------------------")
        clean_tmp_folders(masterfolder, slavefolder, mastermergedapk, mastersignedapk)
    time.sleep(3)

def rename_with_template(masterfinalapk):
    final_name_template =NAME_TEMPLATE
    if (masterfinalapk == None or not os.path.exists(masterfinalapk)):
        return
    if (final_name_template == None or len(final_name_template) <= 0):
        final_name_template = "{apklabel}_Release_v{vername}_{vercode}_{datetime}.apk"
    apk_info = get_app_info(masterfinalapk)
    final_apk_name = masterfinalapk
    if "apklabel" in apk_info:
        try:
            final_apk_name = final_name_template.replace(FORMAT_LABEL, apk_info["apklabel"])
        except:
            Log.out("[Logging...] %s can not be found in %s" % (FORMAT_LABEL, NAME_TEMPLATE))
    if "vername" in apk_info:
        try:
            final_apk_name = final_apk_name.replace(FORMAT_VERNAME, apk_info["vername"])
        except:
            Log.out("[Logging...] %s can not be found in %s" % (FORMAT_VERNAME, NAME_TEMPLATE))
    if "vercode" in apk_info:
        try:
            final_apk_name = final_apk_name.replace(FORMAT_VERCODE, apk_info["vercode"])
        except:
            Log.out("[Logging...] %s can not be found in %s" % (FORMAT_VERCODE, NAME_TEMPLATE))
    if "datetime" in apk_info:
        try:
            final_apk_name = final_apk_name.replace(FORMAT_DATETIME, apk_info["datetime"])
        except:
            Log.out("[Logging...] %s can not be found in %s" % (FORMAT_DATETIME, NAME_TEMPLATE))
    folder = os.path.dirname(masterfinalapk)
    final_apk_path = os.path.normpath(os.path.join(folder, final_apk_name))
    Log.out("[Logging...] 生成最终文件 : [%s]" % final_apk_path)
    if os.path.exists(final_apk_path):
        os.remove(final_apk_path)
    os.rename(masterfinalapk, final_apk_path)

def merge_according_cmdline(args):
    if (len(args) < 2):
        cmd_name = os.path.splitext(os.path.basename(sys.argv[0]))
        p_desc = "             参数描述:"
        c_desc = "             -c 仅检查是否有重复资源"
        d_desc = "             -d 调试模式保留中间文件"
        Log.out("[Logging...] 缺少参数: %s [-c] [-d] apk1 apk2\n%s\n%s\n%s" % (cmd_name[0], p_desc, c_desc, d_desc), True);
        sys.exit()
    masterapk = os.path.abspath(args[0])
    slaveapk = os.path.abspath(args[1])
    mergeapk_batch(masterapk, slaveapk, None, None, None)

def mergeapk_byargs(masterapk, slaveapk, debugmode, outputformat):
    global DEBUG_MODE
    DEBUG_MODE = debugmode
    NAME_TEMPLATE = outputformat
    mergeapk_batch(masterapk, slaveapk, None, None, None)
#############################################################################
if (__name__ == "__main__"):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cdn:")
        for op, value in opts:
            if (op == "-c"):
                CHECK_DUP = True
            elif (op == "-d"):
                DEBUG_MODE = True
            elif (op == "-n"):
                NAME_TEMPLATE = value
    except getopt.GetoptError as err:
        Log.out(err)
        sys.exit()
    merge_according_cmdline(args)