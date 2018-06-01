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

import xlrd
import Log
import Common;

ADPLACES = "adplaces"
ADNAME = "name"
ADPIDS = "pids"
def tran2int(number):
    try:
        return int(number)
    except:
        pass
    return number;

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
    if pids_sheet == None or pids_sheet.nrows < 2:
        return None
    row_header = read_rows(pids_sheet, 0)
    pids_count = pids_sheet.nrows - 1
    for row in range(1, pids_count + 1):
        row_value = read_rows(pids_sheet, row)
        pid = {}
        place_name = row_value[find_index(row_header, ADNAME)]
        has_empty_value = False
        for col in row_header:
            if col == ADNAME:
                continue
            pid[col] = row_value[find_index(row_header, col)]
            if pid[col] == None or len(str(pid[col])) <= 0:
                has_empty_value = True
                continue
            if type(pid[col]) == float:
                pid[col] = tran2int(pid[col])
        if has_empty_value:
            continue
        if place_name in pids_map:
            pids_map[place_name].append(pid)
        else:
            pids_map[place_name] = [pid]

def find_index(header_list, name):
    if header_list == None or len(header_list) <= 0:
        return -1
    return header_list.index(name)

#生成adplace
def generate_adplace(adplaces_sheet, adplaces):
    if adplaces_sheet == None or adplaces_sheet.nrows < 2:
        return None
    row_header = read_rows(adplaces_sheet, 0)
    adplaces_count = adplaces_sheet.nrows - 1
    for row in range(1, adplaces_count + 1):
        row_value = read_rows(adplaces_sheet, row)
        adplace = {}
        has_empty_value = False
        for col in row_header:
            adplace[col] = row_value[find_index(row_header, col)]
            if adplace[col] == None or (len(str(adplace[col])) <= 0):
                has_empty_value = True
                continue
            if type(adplace[col]) == float:
                adplace[col] = tran2int(adplace[col])
        if not has_empty_value:
            adplaces.append(adplace)

def find_pids_in_map(pids_map, name):
    return pids_map[name]

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
    adplace_sheet = read_sheet_by_name(excel_obj, ADPLACES)
    if not adplace_sheet:
        Log.out("[Logging...] 无法获取表单 : [%s]" % "adplaces")
        Common.pause()
        sys.exit(0)

    #获取广告位数据
    generate_adplace(adplace_sheet, adplaces)
    for name in sheet_names:
        if name == ADPLACES:
            continue
        #获取各个广告平台配置数据
        parse_pidlist(read_sheet_by_name(excel_obj, name), pids_map)

    adconfig[ADPLACES] = adplaces;

    for adplace in adplaces:
        name = adplace[ADNAME]
        adplace[ADPIDS] = pids_map[name]

    adstring = str(adconfig)
    adstring = adstring.replace("\'", "\"")
    dirname = os.path.dirname(excel_file)
    basename = os.path.basename(excel_file)
    name, ext = os.path.splitext(basename)
    newname = name + ".txt"
    newfile = os.path.join(dirname, newname)
    f = open(newfile, "w")
    f.write(str(adstring))
    f.close()
    Log.out("[Logging...] 文件转换成功 : [%s]" % newfile)
    Common.pause()

if __name__ == "__main__":
    read_excel(sys.argv[1])