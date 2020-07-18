'''
Created on 2019-8-16

@author: Administrator
'''
from translators_api.google import *
from translators_api.config import *
from collections import OrderedDict
import json
import xml.etree.ElementTree as ET
#from xml.etree import cElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import Document
import os
import sys

## Get pretty look
def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem

def calc_maxlen(all_language):
    max_len = 0
    for key in all_language.keys():
        if all_language[key] != None:
            ilen = len(all_language[key].split("|")[1])
            if ilen > max_len:
                max_len = ilen
    return max_len

def calc_attrib_maxlen(children):
    max_len = 0
    for key in children:
        if key != None and "name" in key.attrib:
            ilen = len(key.attrib["name"])
            if ilen > max_len:
                max_len = ilen
    return max_len
def show_all_support_language():
    max_column = 4
    max_len = calc_maxlen(LANGUAGES)
    all_languages = LANGUAGES.keys()
    index = 1
    column_width = max_len * 2 + 14 + 4
    sys.stdout.write("+")
    sys.stdout.write("-" * (column_width * max_column - 1))
    sys.stdout.write("+\n")
    for item in all_languages:
        c = LANGUAGES[item].split("|")[1]
        leftspace = max_len - len(c)
        space = (2 * leftspace + 2) * " "
        if index % max_column == 0:
            newl = "\n"
        else:
            newl = ""
        if index % max_column == 1:
            line = "|"
        else:
            line = ""
        sys.stdout.write("%s%3d : %s%s%8s |%s" % (line, index, c, space, item, newl))
        #if newl == "\n":
        #    sys.stdout.write("+")
        #    sys.stdout.write("-" * (column_width * max_column - 1))
        #    sys.stdout.write("+\n")
        index += 1
    if len(all_languages) % max_column != 0:
        sys.stdout.write("\n")
    sys.stdout.write("+")
    sys.stdout.write("-" * (column_width * max_column - 1))
    sys.stdout.write("+\n")

def translate(text, from_language, to_language):
    try:
        return google_api(text, from_language=from_language, to_language=to_language)
    except:
        pass
    return None

def input_no(prompt, auto = False):
    list_keys= [ key for key in LANGUAGES.keys()]
    try:
        while True:
            if auto:
                raw_str = input(prompt) or "auto"
            else:
                raw_str = input(prompt)
            if raw_str != None and raw_str in list_keys:
                return raw_str
    except:
        print("")
    return None

def input_language():
    from_language = input_no("[Logging...] 请输入源语言(默认auto)：", True)
    if from_language == None or len(from_language) <= 0:
        from_language = "auto"
    to_language = input_no("[Logging...] 请输入目标语言：")
    if from_language == None or to_language == None:
        sys.exit(0)
    print("[Logging...] 待翻译语言 : [%s(%s)] -> 目标语言 : [%s(%s)]" % (LANGUAGES[from_language].split("|")[1] , from_language, LANGUAGES[to_language].split("|")[1] , to_language))
    return from_language, to_language

def translate_xml(from_language, to_language, xmlfile):
    #创建目标文档 start
    filedir = os.path.dirname(xmlfile)
    basename = os.path.basename(xmlfile)
    to_dir = "values-%s" % to_language
    dst_dir = os.path.join(filedir, to_dir)
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    dstfile = os.path.join(dst_dir, basename)
    toDoc = Document()  #创建DOM文档对象
    toRoot = toDoc.createElement('resources') #创建根元素
    toDoc.appendChild(toRoot)
    #创建目标文档 end
    try:
        fromTree = ET.parse(xmlfile)
    except:
        print("[Logging...] 文件解析错误[%s]" % xmlfile)
        return
    fromRoot = fromTree.getroot()
    children = list(fromRoot)
    max_len = calc_attrib_maxlen(children)
    index = 1
    print("-----------------------------------------------------------------------")
    for child in children:
        if not "name" in child.attrib:
            continue
        space = (max_len - len(child.attrib["name"])) * " "
        if ("translatable" in child.attrib and child.attrib["translatable"] == "false"):
            print("%3s. %s%s : %s -> %s" % (index, child.attrib["name"], space, child.text, "不需要翻译"))
            continue
        if child.text == None or len(child.text) <= 0:
            continue
        result = translate(child.text, from_language, to_language)
        try:
            print("%3s. %s%s : %s -> %s" % (index, child.attrib["name"], space, child.text, result))
        except Exception as e:
            print("%3s. %s%s : %s -> %s" % (index, child.attrib["name"], space, child.text, "输出结果异常：[%s]" % e))
        if result != None and len(result) > 0:
            element = toDoc.createElement("string")
            element.setAttribute("name", child.attrib["name"])
            textNode = toDoc.createTextNode(result)
            element.appendChild(textNode)
            toRoot.appendChild(element)
            index = index + 1
    print("-----------------------------------------------------------------------")
    print("[Logging...] 翻译字符数量 : [%s]" % len(toRoot.childNodes))
    if not toRoot.hasChildNodes():
        return
    print("[Logging...] 正在写入文件 : [%s]" % dstfile)
    if os.path.exists(dstfile):
        os.remove(dstfile)
    f = open(dstfile,'wb')
    f.write(toDoc.toxml(encoding="utf-8"))
    f.close()
    atree = ET.parse(dstfile)
    aroot = atree.getroot()
    indent(aroot)
    atree.write(dstfile, encoding='utf-8', xml_declaration=True)
    print("[Logging...] 写入文件完成 : [%s]" % dstfile)

if (__name__ == "__main__"):
    
    if (len(sys.argv) < 2):
        print("缺少参数 %s <string.xml>" % os.path.basename(sys.argv[0]))
        sys.exit(0)
    xmlfile = sys.argv[1]
if not os.path.exists(xmlfile):
        print("%s 不存在" % xmlfile)
        sys.exit(0)
show_all_support_language()
from_language, to_language = input_language()
translate_xml(from_language, to_language, xmlfile)
sys.exit(0)
#后续可以读取xml，然后翻译之后，在写入xml