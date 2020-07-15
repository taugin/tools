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
import subprocess
import shutil
import getopt
import Utils
import Common
import re
import xml.etree.ElementTree as ET
from xml.etree import cElementTree as ET

STATIC_FIELD_RE = re.compile(".field public static final (.*?):I = (0x\d+)", 0)

def adjust_match_rfile(f):
    static_fields = []
    file = open(f, "r")
    lines = file.readlines()
    if lines == None or len(lines) <= 0:
        return False
    if not lines[0].startswith(".class public final "):
        return False
    startStaticField = False
    for line in lines:
        if line == None:
            continue
        line = line.strip()
        if len(line) <= 0:
            continue
        if line == "# static fields":
            startStaticField = True
            continue
        if startStaticField:
            static_fields.append(line)

    if static_fields == None or len(static_fields) <= 0:
        return False

    for s in static_fields:
        result = STATIC_FIELD_RE.match(s)
        if not result:
            return False
    return True

def find_all_rfiles(smali_folder):
    '''查找疑似R文件'''
    rtmp = []
    file_list = os.walk(smali_folder, True)
    for root, filedir, files in file_list:
        for file in files:
            tmpfile = os.path.join(root, file)
            match_rfile = adjust_match_rfile(tmpfile)
            if (match_rfile):
                rtmp.append(tmpfile)
    return rtmp

def update_layout_type(masterfolder, fromname, toname):
    '''还原layout资源'''
    update_layout_file = False
    resdir = os.path.join(masterfolder, "res")
    alldir = os.listdir(resdir)
    layoutdir = []
    if (alldir != None and len(alldir) > 0):
        for d in alldir:
            if (d != None and d.startswith("layout")):
                layoutdir.append(d)
    for ldir in layoutdir:
        fromfile = os.path.join(masterfolder, "res", ldir, fromname + ".xml")
        tofile = os.path.join(masterfolder, "res", ldir, toname + ".xml")
        if (os.path.exists(fromfile) and fromfile != tofile):
            Log.out("Update layout res : %s --> %s" % (fromname, toname))
            Utils.movefile(fromfile, tofile)
            update_layout_file = True
    return update_layout_file

def update_attr_type(masterfolder, fromname, toname): 
    update_attr = False
    attr_file = os.path.join(masterfolder, "res", "values", "attrs.xml")
    tree = ET.parse(attr_file)
    root = tree.getroot()
    attr_item = root.find("attr/[@name='%s']" % fromname)
    if attr_item != None:
        attr_item.attrib["name"] = toname
        tree.write(attr_file, encoding='utf-8', xml_declaration=True)
        update_attr = True
        Log.out("Update attr res : %s --> %s" % (fromname, toname))
    return update_attr

def update_res_through_type(masterfolder, name, resid, pubroot, modtype):
    pubitem = pubroot.find("public/[@id='%s']" % (resid))
    if (pubitem != None and pubitem.attrib["type"] == modtype):
        srcname = pubitem.attrib["name"]
        if (name == srcname):
            return
        update_success = False
        if (modtype == "layout"):
            update_success = update_layout_type(masterfolder, srcname, name)
        elif (modtype == "attr"):
            update_success = update_attr_type(masterfolder, srcname, name)

        if (update_success):
            pubitem.attrib["name"] = name

def update_rfiles(masterfolder, rfile, pubroot):
    all_static_fields = find_all_static_fields(rfile)
    for field in all_static_fields:
        name, value = find_name_value_pair(field)
        if (name != None and value != None):
            update_res_through_type(masterfolder, name,value, pubroot, "attr")

def update_all_rfiles(masterfolder):
    publicxml = os.path.join(masterfolder, "res", "values", "public.xml")
    if (not os.path.exists(publicxml)):
        return
    tree = ET.parse(publicxml)
    pubroot = tree.getroot()

    smali_folder = os.path.join(masterfolder, "smali")
    all_rfiles = find_all_rfiles(smali_folder)
    if all_rfiles != None and len(all_rfiles) > 0:
        for rfile in all_rfiles:
            update_rfiles(masterfolder, rfile, pubroot)

    smali_folder = os.path.join(masterfolder, "smali_classes2")
    all_rfiles = find_all_rfiles(smali_folder)
    if all_rfiles != None and len(all_rfiles) > 0:
        for rfile in all_rfiles:
            update_rfiles(masterfolder, rfile, pubroot)

    tree.write(publicxml, encoding='utf-8', xml_declaration=True)
#================================================================================
def find_name_value_pair(field):
    '''查找常量字段名称和值'''
    if (field == None or len(field) <= 0):
        return None
    field = field.strip()
    s = field.split(" ")
    if (s != None and len(s) == 7):
        name = s[4][0:-2]
        value = s[6]
        return (name, value)
    return None

def find_all_static_fields(rfile):
    '''查询R文件的所有常量'''
    all_static_fields = []
    f = open(rfile, "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        if (line != None and line.startswith(".field public static final ")):
            all_static_fields.append(line)
    return all_static_fields

def find_map_between_public_and_rfile(pubroot, rfile):
    '''结合public.xml读取混淆前后的名字'''
    all_static_fields = find_all_static_fields(rfile)
    map_dict = {}
    for field in all_static_fields:
        srcname, resid = find_name_value_pair(field)
        pubitem = pubroot.find("public/[@id='%s']" % resid)
        if (pubitem != None):
            obfname = pubitem.attrib["name"]
            restype = pubitem.attrib["type"]
            map_dict[obfname + "__" + restype] = [srcname, obfname, restype]
    return map_dict

def generate_mapping(masterfolder, all_rfiles):
    '''生成混淆映射表'''
    pubxml = os.path.join(masterfolder, "res", "values", "public.xml")
    tree = ET.parse(pubxml)
    root = tree.getroot()
    map_dict = {}
    for rfile in all_rfiles:
        tmp_dict = find_map_between_public_and_rfile(root, rfile)
        map_dict.update(tmp_dict)
    return map_dict

def rename_all_files(masterfolder, map_dict = None):
    Log.out("[Logging...] 更新资源文件名称")
    resdir = os.path.join(masterfolder, "res")
    mylist = os.walk(resdir, True)
    for root, filedir, files in mylist:
        for file in files:
            dirroot = os.path.basename(root)
            dirtype = dirroot.split("-")[0]
            if dirtype == "values":
                continue
            filebase, ext = os.path.splitext(file)
            map_value = get_map_value(filebase, dirtype, map_dict)
            if (map_value != None and len(map_value) > 0):
                srcname = map_value[0]
                fromfile = os.path.join(root, file)
                tofile = os.path.join(root, srcname + ext)
                Utils.movefile(fromfile, tofile)

def update_public_file(masterfolder, map_dict):
    Log.out("[Logging...] 更新public文件")
    attrs_file = os.path.join(masterfolder, "res", "values", "public.xml")
    tree = ET.parse(attrs_file)
    root = tree.getroot()
    for child in root.getchildren():
        obfname = child.attrib["name"]
        restype = child.attrib["type"]
        map_value = map_value = get_map_value(obfname, restype, map_dict)
        if map_value != None and len(map_value) > 0:
            srcname = map_value[0]
            child.attrib["name"] = srcname
    tree.write(attrs_file, encoding='utf-8', xml_declaration=True)

def get_map_value(obfname, restype, map_dict):
    map_value = None
    try :
        map_value = map_dict[obfname + "__" + restype]
    except:
        pass
    return map_value

def process_xml(node, tag, attrib, text, map_dict, file):
    for attr in attrib:
        Log.out("%s[%s] : %s | %s" % (tag, attr, attrib[attr], file))

def walk_xml_data(root, map_dict, file):
    if root == None:
        return
    tag = root.tag
    attrib = root.attrib
    text = root.text and root.text.strip()
    process_xml(root, tag, attrib, text, map_dict, file)
    children_nodes = root.getchildren()
    if children_nodes != None and len(children_nodes) > 0:
        for child in children_nodes:
            walk_xml_data(child, map_dict, file)

def traversal_res(masterfolder, map_dict = None):
    resdir = os.path.join(masterfolder, "res")
    mylist = os.walk(resdir, True)
    for root, filedir, files in mylist:
        for file in files:
            if not file.endswith(".xml"):
                continue
            tmpfile = os.path.join(root, file)
            tree = ET.parse(tmpfile)
            walk_xml_data(tree.getroot(), map_dict, tmpfile)

def res_recovery(masterfolder):
    smali_folder_list = ["smali", "smali_classes2"]
    all_rfiles = []
    for s in smali_folder_list:
        all_rfiles += find_all_rfiles(os.path.join(masterfolder, s))
    if (len(all_rfiles) <= 0):
        Log.out("[Erroring ...] 没有找到R文件")
        return
    map_dict = generate_mapping(masterfolder, all_rfiles)
    if (map_dict == None or len(map_dict) <= 0):
        Log.out("[Erroring ...] 无法生成影射文件")
        return

    #rename_all_files(masterfolder, map_dict)
    traversal_res(masterfolder, map_dict)
    #update_public_file(masterfolder, map_dict)

if __name__ == "__main__":
    traversal_res("F:\\myprojects\\smalicode\\Clothes_outlet")