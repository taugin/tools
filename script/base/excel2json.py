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
import hashlib

#描述广告位名称
AD_PLACES = "adplaces"
#描述表单之间关联的值
AD_NAME = "name"
#描述所有广告位
AD_PIDS = "pids"
#pidlist
PLACE_LIST = "placelist"
#adids
ADIDS = "adids"
#gtconfig
GTCONFIG = "gtconfig"
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

SHOW_FIELD = "show"

#################################for arguement#################################
REGISTER_TO_REGISTRY = False
ONLY_ENCRYPT = False
ONLY_DECRYPT = False
INPUT_FILE = None
PRO_ID = None
PRO_NAME = None
PRO_PKG = None
###############################################################################


def log(msg):
    print(msg)

def pause():
    input("按回车键退出...")

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
        show_adplace = row_value[find_index(header_row_key, SHOW_FIELD)]
        if (show_adplace != None and show_adplace == 0):
            continue
        for col_key in header_row_key:
            '''show字段不加入配置文件'''
            if col_key == SHOW_FIELD:
                continue
            adplace[col_key] = row_value[find_index(header_row_key, col_key)]
            col_type = header_row_type[find_index(header_row_key, col_key)]
            col_constrait = header_row_constraint[find_index(header_row_key, col_key)]
            if adplace[col_key] == None or (len(str(adplace[col_key])) <= 0):
                if col_constrait == NOT_NULL_VALUE:
                    has_empty_value = True
                    log("[Logging...] 发现空白字段 : [%s]" % col_key)
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

def generate_singleconfig(adplaces_sheet, singleconfig):
    if adplaces_sheet == None or adplaces_sheet.nrows < HEADER_ROWS_COUNT + 1:
        return None
    header_row_key = read_rows(adplaces_sheet, HEADER_KEY_POS)
    header_row_type = read_rows(adplaces_sheet, HEADER_TYPE_POS)
    header_row_constraint = read_rows(adplaces_sheet, HEADER_CONSTRAINT_POS)
    adplaces_count = adplaces_sheet.nrows - HEADER_ROWS_COUNT

    for row in range(HEADER_ROWS_COUNT, adplaces_count + HEADER_ROWS_COUNT):
        row_value = read_rows(adplaces_sheet, row)
        for col_key in header_row_key:
            singleconfig[col_key] = row_value[find_index(header_row_key, col_key)]
            col_type = header_row_type[find_index(header_row_key, col_key)]
            col_constrait = header_row_constraint[find_index(header_row_key, col_key)]
            if singleconfig[col_key] == None or (len(str(singleconfig[col_key])) <= 0):
                if col_constrait == NOT_NULL_VALUE:
                    log("[Logging...] 发现空白字段 : [%s]" % col_key)
                    continue
                else:
                    try :
                        singleconfig.pop(col_key)
                    except:
                        pass
            else:
                singleconfig[col_key] = format_value(singleconfig[col_key], col_type)

def string_md5(md5str):
    if (md5str != None and len(md5str) > 0):
        md5=hashlib.md5(md5str.encode('utf-8')).hexdigest()
        return md5
    return None

def read_excel(excel_file):
    log("[Logging...] 文件格式转换 : [%s]" % input_file)
    if (input_file == None or len(input_file) <= 0):
        log("[Logging...] 缺少表格文件")
        sys.exit(0)
    adconfig = collections.OrderedDict()
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

    #获取adplaces工作表###################################
    adplace_sheet = read_sheet_by_name(excel_obj, AD_PLACES)
    if not adplace_sheet:
        log("[Logging...] 无法获取表单 : [%s]" % AD_PLACES)
        pause()
        sys.exit(0)

    #获取广告位数据
    generate_adplace(adplace_sheet, adplaces)
    sheet_sdk = read_sheet_by_name(excel_obj, PLACE_LIST)
    if (sheet_sdk != None):
        parse_pidlist(sheet_sdk, pids_map)
    else:
        log("[Error.....] 无法获取表单 : [%s]" % PLACE_LIST)
        pause()
        sys.exit(0)

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
    #######################################################

    for name in sheet_names:
        if name == AD_PLACES or name == PLACE_LIST:
            continue
        adplace_sheet = read_sheet_by_name(excel_obj, name)
        if (adplace_sheet.visibility != 0):
            continue
        if not adplace_sheet:
            log("[Logging...] 无法获取表单 : [%s]" % name)
        config = collections.OrderedDict()
        try:
            generate_singleconfig(adplace_sheet, config)
        except Exception as e:
            log("[Logging...] %s" % e)
        if (len(config) > 0):
            adconfig[name] = config;
            log("[Logging...] 获取配置成功 : [%s]" % name)
        else:
            log("[Logging...] 获取配置失败 : [%s]" % name)

    #######################################################
    adplace = adconfig.pop(AD_PLACES)
    adconfig[AD_PLACES] = adplace
    #######################################################
    adstring = str(adconfig)
    adstring = adstring.replace("\'", "\"")
    dirname = os.path.dirname(excel_file)
    basename = os.path.basename(excel_file)
    name, ext = os.path.splitext(basename)
    newname = "data_config.json"
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
if __name__ == "__main__":
    input_file = None
    if (len(sys.argv) > 1):
        input_file = sys.argv[1]
    read_excel(input_file)