#!/usr/bin/python
# coding: UTF-8
import sys
import os
from builtins import float
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import json
import xlrd
import Log
import Common;

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
    Log.out("cell type : %s" % cell.ctype)

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
        pid = {}
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
    adplaces_count = adplaces_sheet.nrows - HEADER_ROWS_COUNT
    for row in range(HEADER_ROWS_COUNT, adplaces_count + HEADER_ROWS_COUNT):
        row_value = read_rows(adplaces_sheet, row)
        adplace = {}
        has_empty_value = False
        for col_key in header_row_key:
            adplace[col_key] = row_value[find_index(header_row_key, col_key)]
            col_type = header_row_type[find_index(header_row_key, col_key)]
            if adplace[col_key] == None or (len(str(adplace[col_key])) <= 0):
                has_empty_value = True
                Log.out("[Logging...] 发现空白字段: [%s]" % col_key)
                continue
            adplace[col_key] = format_value(adplace[col_key], col_type)
        if not has_empty_value:
            adplaces.append(adplace)

def read_excel(excel_file):
    adconfig = {}
    adplaces = []
    pids_map = {}
    if not os.path.exists(excel_file):
        Log.out("[Logging...] 无法定位文件 : [%s]" % excel_file)
        Common.pause()
        sys.exit(0)

    excel_obj = open_excel(excel_file)
    if not excel_obj:
        Log.out("[Logging...] 无法解析文件 : [%s]" % excel_file)
        Common.pause()
        sys.exit(0)

    sheet_names = read_sheet_names(excel_obj)
    if not sheet_names:
        Log.out("[Logging...] 无法解析表单 : [%s]" % excel_file)
        Common.pause()
        sys.exit(0)

    #获取adplaces工作表
    adplace_sheet = read_sheet_by_name(excel_obj, AD_PLACES)
    if not adplace_sheet:
        Log.out("[Logging...] 无法获取表单 : [%s]" % "adplaces")
        Common.pause()
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
            Log.out("[Logging...] 处理广告位中 : [%s - %s]" % (name, len(adplace[AD_PIDS])))
        except:
            Log.out("[Error.....] 无法找到健值 : [%s]" % name)
            #Common.pause()
            #sys.exit(0)

    if (adplaces != None):
        Log.out("[Logging...] 广告位总个数 : [%s]" % len(adplaces))
    adstring = str(adconfig)
    adstring = adstring.replace("\'", "\"")
    dirname = os.path.dirname(excel_file)
    basename = os.path.basename(excel_file)
    name, ext = os.path.splitext(basename)
    newname = name + ".txt"
    newfile = os.path.join(dirname, newname)
    output = str(adstring)
    try:
        output = json.dumps(adconfig, indent=4)
    except:
        output = str(adstring)
    f = open(newfile, "w")
    f.write(output)
    f.close()
    Log.out("[Logging...] 文件转换成功 : [%s]" % newfile)
    Common.pause()

if __name__ == "__main__":
    read_excel(sys.argv[1])