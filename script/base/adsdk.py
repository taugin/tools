#!/usr/bin/python
# coding: UTF-8
import sys
import os
from builtins import float
#引入别的文件夹的模块

import json
import xlrd
import collections
import getopt
import subprocess
import winreg

#描述广告位名称
AD_PLACES = "adplaces"
#描述表单之间关联的值
AD_NAME = "name"
#描述所有广告位
AD_PIDS = "pids"
#表示表头的行数
HEADER_ROWS_COUNT = 4
#表示内容开始的位置
CONTENT_START_POS = 4
#表示健值的表头位置
HEADER_KEY_POS = 0
#表示类型的健值位置
HEADER_TYPE_POS = 1;
#表示约束控制的健值位置
HEADER_CONSTRAINT_POS = 2
#表示描述信息的健值位置
HEADER_DESC_POS = 3

NULL_VALUE = "null"

NOT_NULL_VALUE = "notnull"

#################################for arguement#################################
REGISTER_TO_REGISTRY = False
ONLY_ENCRYPT = False
ONLY_DECRYPT = False
INPUT_FILE = None
PRO_ID = None
###############################################################################


def log(msg):
    print(msg)

def pause():
    input("按回车键退出...")

def find_proid_from_filename():
    if (INPUT_FILE == None or len(INPUT_FILE)) <= 0:
        return None
    product_name = None
    try:
        file_name = os.path.basename(INPUT_FILE)
        file_name= os.path.splitext(file_name)[0]
        if (file_name.find("_") > -1):
            product_name = file_name.split("_")[-1]
    except:
        pass
    return product_name
def find_proid_from_pidname(pid):
    if pid == None or len(pid) <= 0:
        return None
    try:
        index = pid.rfind("/")
        seg3 = pid[index + 1:]
        return seg3.split("-")[0]
    except Exception as e:
        pass #log("e : %s" % e)
    return None

def check_product(pid, sdk):
    if (sdk != "dfp"):
        #log("[Logging...] 忽略产品检查 : [%s]" % sdk)
        return
    if PRO_ID == None or len(PRO_ID) <= 0:
        return
    proid_frompid = find_proid_from_pidname(pid)
    if proid_frompid == None or len(proid_frompid) <= 0:
        log("[Logging...] 缺少产品编号 : [%s] : [%s]" % (sdk, pid))
        return
    if PRO_ID != proid_frompid:
        log("[Logging...] 产品编号异常 : [%s] : [%s] : [%s]" % (PRO_ID, proid_frompid, pid))

def format_value(origin, col_type):
    try:
        if col_type == "int":
            return int(origin)
        if col_type == "float":
            return float(origin)
        if col_type == "object":
            return json.loads(origin)
    except:
        pass
    return origin

def read_rows(sheet_table, row):
    '''Read row values'''
    return sheet_table.row_values(row)

def read_cols(sheet_table, col):
    '''Read col values'''
    return sheet_table.col_values(col)

def read_cell(sheet_table, row, col):
    '''Read cell values'''
    return sheet_table.cell_value(row,col);

def read_sheet_names(excel_obj):
    '''Read all sheets'''
    return excel_obj.sheet_names()

def read_sheet_by_name(excel_obj, name):
    '''Read sheet by name'''
    try:
        return excel_obj.sheet_by_name(name)
    except:
        pass
    return None

def read_sheet_by_index(excel_obj, index):
    '''Read sheet by index'''
    return excel_obj.sheet_by_index(index)

def show_cell_type(cell):
    log("cell type : %s" % cell.ctype)

def open_excel(excel_file):
    try:
        return xlrd.open_workbook(excel_file)
    except:
        pass
    return None

def parse_pidlist(pids_sheet, pids_map):
    if pids_sheet == None or pids_sheet.nrows < HEADER_ROWS_COUNT + 1:
        return None
    header_row_key = read_rows(pids_sheet, HEADER_KEY_POS)
    header_row_type = read_rows(pids_sheet, HEADER_TYPE_POS)
    header_row_constraint = read_rows(pids_sheet, HEADER_CONSTRAINT_POS)
    pids_count = pids_sheet.nrows - HEADER_ROWS_COUNT
    for row in range(CONTENT_START_POS, pids_count + HEADER_ROWS_COUNT):
        row_value = read_rows(pids_sheet, row)
        pid = collections.OrderedDict()
        place_name = row_value[find_index(header_row_key, AD_NAME)]
        has_empty_value = False
        for col in header_row_key:
            if col == AD_NAME:
                continue
            pid[col] = row_value[find_index(header_row_key, col)]
            col_type = header_row_type[find_index(header_row_key, col)]
            col_constrait = header_row_constraint[find_index(header_row_key, col)]

            if (pid[col] == None or len(str(pid[col])) <= 0):
                if col_constrait == NOT_NULL_VALUE:
                    has_empty_value = True
                elif col_constrait == NULL_VALUE:
                    try :
                        pid.pop(col)
                    except:
                        pass
            else:
                pid[col] = format_value(pid[col], col_type)
        if has_empty_value:
            continue
        if place_name in pids_map:
            pids_map[place_name].append(pid)
        else:
            pids_map[place_name] = [pid]
        if pid != None and "sdk" in pid and "pid" in pid:
            check_product(pid["pid"], pid["sdk"])

def find_index(header_list, name):
    '''查找key值所在的index'''
    if header_list == None or len(header_list) <= 0:
        return -1
    if name in header_list:
        return header_list.index(name)
    return None

#生成adplace
def generate_adplace(adplaces_sheet, adplaces):
    if adplaces_sheet == None or adplaces_sheet.nrows < HEADER_ROWS_COUNT + 1:
        return None
    header_row_key = read_rows(adplaces_sheet, HEADER_KEY_POS)
    header_row_type = read_rows(adplaces_sheet, HEADER_TYPE_POS)
    header_row_constraint = read_rows(adplaces_sheet, HEADER_CONSTRAINT_POS)
    adplaces_count = adplaces_sheet.nrows - HEADER_ROWS_COUNT
    for row in range(HEADER_ROWS_COUNT, adplaces_count + HEADER_ROWS_COUNT):
        row_value = read_rows(adplaces_sheet, row)
        adplace = collections.OrderedDict()
        has_empty_value = False
        for col_key in header_row_key:
            adplace[col_key] = row_value[find_index(header_row_key, col_key)]
            col_type = header_row_type[find_index(header_row_key, col_key)]
            col_constrait = header_row_constraint[find_index(header_row_key, col_key)]
            if adplace[col_key] == None or (len(str(adplace[col_key])) <= 0):
                if col_constrait == NOT_NULL_VALUE:
                    has_empty_value = True
                    log("[Logging...] 发现空白字段: [%s]" % col_key)
                    continue
                else:
                    try :
                        adplace.pop(col_key)
                    except:
                        pass
            else:
                adplace[col_key] = format_value(adplace[col_key], col_type)
        if not has_empty_value:
            adplaces.append(adplace)

def read_excel(excel_file):
    if (input_file == None or len(input_file) <= 0):
        log("[Logging...] 缺少表格文件 : [%s]" % input_file)
        sys.exit(0)

    global PRO_ID
    PRO_ID = find_proid_from_filename()
    if PRO_ID == None or len(PRO_ID) <= 0:
        log("[Logging...] 缺少产品编号 : [%s]" % input_file)
    else:
        log("[Logging...] 当前产品编号 : [%s]" % PRO_ID)

    adconfig = {}
    adplaces = []
    pids_map = collections.OrderedDict()
    if not os.path.exists(excel_file):
        log("[Logging...] 无法定位文件 : [%s]" % excel_file)
        pause()
        sys.exit(0)

    excel_obj = open_excel(excel_file)
    if not excel_obj:
        log("[Logging...] 无法解析文件 : [%s]" % excel_file)
        pause()
        sys.exit(0)

    sheet_names = read_sheet_names(excel_obj)
    if not sheet_names:
        log("[Logging...] 无法解析表单 : [%s]" % excel_file)
        pause()
        sys.exit(0)

    #获取adplaces工作表
    adplace_sheet = read_sheet_by_name(excel_obj, AD_PLACES)
    if not adplace_sheet:
        log("[Logging...] 无法获取表单 : [%s]" % "adplaces")
        pause()
        sys.exit(0)

    #获取广告位数据
    generate_adplace(adplace_sheet, adplaces)
    for name in sheet_names:
        if name == AD_PLACES:
            continue
        #获取各个广告平台配置数据
        sheet_sdk = read_sheet_by_name(excel_obj, name)
        #只处理可见的表单
        if (sheet_sdk.visibility == 0):
            parse_pidlist(sheet_sdk, pids_map)

    adconfig[AD_PLACES] = adplaces;

    for adplace in adplaces:
        name = adplace[AD_NAME]
        try:
            adplace[AD_PIDS] = pids_map[name]
            log("[Logging...] 处理广告位中 : [%s - %s]" % (name, len(adplace[AD_PIDS])))
        except:
            log("[Error.....] 无法找到健值 : [%s]" % name)
            #pause()
            #sys.exit(0)

    if (adplaces != None):
        log("[Logging...] 广告位总个数 : [%s]" % len(adplaces))
    adstring = str(adconfig)
    adstring = adstring.replace("\'", "\"")
    dirname = os.path.dirname(excel_file)
    basename = os.path.basename(excel_file)
    name, ext = os.path.splitext(basename)
    newname = name + ".txt"
    newfile = os.path.join(dirname, newname)
    output = str(adstring)
    try:
        output = json.dumps(adconfig, sort_keys=False, indent=4)
    except:
        output = str(adstring)
    f = open(newfile, "w")
    f.write(output)
    f.close()
    log("[Logging...] 文件转换成功 : [%s]" % newfile)
    pause()
###############################################################################
def find_aes_file():
    aes_dir = os.getcwd()
    aes_file = os.path.join(aes_dir, "aes.jar")
    if os.path.exists(aes_file):
        return aes_file
    aes_dir = os.path.dirname(sys.argv[0])
    aes_file = os.path.join(aes_dir, "aes.jar")
    if os.path.exists(aes_file):
        return aes_file
    return None

def find_java_file():
    try:
        home = os.environ.get("PATH")
        patharray = home.split(os.pathsep)
        for p in patharray:
            java_file = os.path.join(p, "java.exe")
            if os.path.exists(java_file):
                return java_file
    except:
        pass
    return None

def encrypt_config_file(input_file):
    if (input_file == None or len(input_file) <= 0):
        log("[Logging...] 缺少明文文件 : [%s]" % input_file)
        sys.exit(0)
    output_file = None
    key = "123456789"
    if input_file == None or not os.path.exists(input_file):
        return
    input_file = os.path.normpath(input_file)
    if output_file == None or not os.path.exists(output_file):
        basename = os.path.basename(input_file)
        name, ext= os.path.splitext(basename)
        output_file = "%s-encrypt%s" % (name, ext)
    aes_file = find_aes_file()
    if (aes_file == None):
        log("[Logging...] 无法找到文件 : [aes.jar]")
        pause()
        return
    java_file = find_java_file()
    if (java_file == None):
        log("[Logging...] 无法找到文件 : [java]")
        pause()
        return
    log("[Logging...] 加密文件 : [%s],  key : [%s], output : [%s]\n" % (aes_file, key, output_file))
    cmdlist = [java_file, "-jar", aes_file, "-e", "-k", key, "-i", input_file, "-o", output_file]
    subprocess.call(cmdlist)
    pause()

def decrypt_config_file(input_file):
    if (input_file == None or len(input_file) <= 0):
        log("[Logging...] 缺少密文文件 : [%s]" % input_file)
        sys.exit(0)
    output_file = None
    key = "123456789"
    if input_file == None or not os.path.exists(input_file):
        return
    input_file = os.path.normpath(input_file)
    if output_file == None or not os.path.exists(output_file):
        basename = os.path.basename(input_file)
        name, ext= os.path.splitext(basename)
        output_file = "%s-decrypt%s" % (name, ext)

    aes_file = find_aes_file()
    if (aes_file == None):
        log("[Logging...] 无法找到文件 : [aes.jar]")
        pause()
        return
    java_file = find_java_file()
    if (java_file == None):
        log("[Logging...] 无法找到文件 : [java]")
        pause()
        return
    log("[Logging...] 解密文件 : [%s],  key : [%s], output : [%s]\n" % (aes_file, key, output_file))
    cmdlist = [java_file, "-jar", aes_file, "-d", "-k", key, "-i", input_file, "-o", output_file]
    subprocess.call(cmdlist)
    pause()


def add_xlsx2json_registry():
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell")
    sub_key1 = winreg.CreateKey(key, r"ADSDK转换")
    #icon = sys.argv[0] + " , 0"
    #winreg.SetValue(sub_key1, "Icon", winreg.REG_SZ, icon)
    if sys.argv[0].endswith(".py"):
        command = "python " + sys.argv[0] + " \"%1\""
    else:
        command = sys.argv[0] + " \"%1\""
    sub_key2 = winreg.CreateKey(sub_key1, r"command")
    winreg.SetValue(sub_key2, r"", winreg.REG_SZ, command)

def add_encrypt_registry():
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell")
    sub_key1 = winreg.CreateKey(key, r"ADSDK加密")
    #icon = sys.argv[0] + " , 0"
    #winreg.SetValue(sub_key1, "Icon", winreg.REG_SZ, icon)
    if sys.argv[0].endswith(".py"):
        command = "python " + sys.argv[0] + " -e \"%1\""
    else:
        command = sys.argv[0] + " -e \"%1\""
    sub_key2 = winreg.CreateKey(sub_key1, r"command")
    winreg.SetValue(sub_key2, r"", winreg.REG_SZ, command)

def add_dncrypt_registry():
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell")
    sub_key1 = winreg.CreateKey(key, r"ADSDK解密")
    #icon = sys.argv[0] + " , 0"
    #winreg.SetValue(sub_key1, "Icon", winreg.REG_SZ, icon)
    if sys.argv[0].endswith(".py"):
        command = "python " + sys.argv[0] + " -d \"%1\""
    else:
        command = sys.argv[0] + " -d \"%1\""
    sub_key2 = winreg.CreateKey(sub_key1, r"command")
    winreg.SetValue(sub_key2, r"", winreg.REG_SZ, command)

def register_to_registry():
    try:
        add_xlsx2json_registry()
        add_encrypt_registry()
        add_dncrypt_registry()
        log("[Logging...] 注册功能成功")
    except Exception as e:
        log("[Logging...] 注册功能失败 : [%s]" % e)
    pause()

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "der")
    for op, value in opts:
        if (op == "-r"):
            REGISTER_TO_REGISTRY = True
        elif (op == "-e"):
            ONLY_ENCRYPT = True
        elif (op == "-d"):
            ONLY_DECRYPT = True

    if len(sys.argv[1:]) <= 0:
        REGISTER_TO_REGISTRY = True
    input_file = None
    if (len(args) >= 1):
        input_file = args[0]
    #log("[Logging...] 变现处理脚本 : 注册功能 : [%s] , 加密 : [%s] , 解密 : [%s] , 输入文件 : [%s]" % (REGISTER_TO_REGISTRY, ONLY_ENCRYPT, ONLY_DECRYPT, input_file))
    INPUT_FILE = input_file
    if REGISTER_TO_REGISTRY:
        register_to_registry()
    elif ONLY_ENCRYPT:
        encrypt_config_file(input_file)
    elif ONLY_DECRYPT:
        decrypt_config_file(input_file)
    else:
        read_excel(input_file)