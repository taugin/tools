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

def input_no(prompt):
    list_keys= [ i for i in LANGUAGES.keys()]
    try:
        while True:
            i = input(prompt)
            if i != None and i in list_keys:
                return i
    except:
        print("")
    return None

def input_language():
    from_language = input_no("请输入源语言：")
    if from_language == None or len(from_language) <= 0:
        from_language = "auto"
    to_language = input_no("请输入目标语言：")
    if from_language == None or to_language == None:
        sys.exit(0)
    print("源语言：%s(%s) -> 目标语言 ：%s(%s)" % (LANGUAGES[from_language].split("|")[1] , from_language, LANGUAGES[to_language].split("|")[1] , to_language))
    return from_language, to_language

def translate_xml(from_language, to_language, xmlfile):
    #创建目标文档 start
    filedir = os.path.dirname(xmlfile)
    to_dir = "values-%s" % to_language
    dst_dir = os.path.join(filedir, to_dir)
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    dstfile = os.path.join(dst_dir, "values.xml")
    toDoc = Document()  #创建DOM文档对象
    toRoot = toDoc.createElement('resources') #创建根元素
    toDoc.appendChild(toRoot)
    #创建目标文档 end
    try:
        fromTree = ET.parse(xmlfile)
    except:
        print("xml文件[%s]解析错误" % xmlfile)
        return
    fromRoot = fromTree.getroot()
    children = list(fromRoot)
    max_len = calc_attrib_maxlen(children)
    index = 1
    for child in children:
        space = (max_len - len(child.attrib["name"])) * " "
        if ("translatable" in child.attrib and child.attrib["translatable"] == "false"):
            print("%3. s%s%s : %s -> %s" % (index, child.attrib["name"], space, child.text, "不需要翻译"))
            continue
        if child.text == None or len(child.text) <= 0:
            continue
        result = translate(child.text, from_language, to_language)
        print("%3s. %s%s : %s -> %s" % (index, child.attrib["name"], space, child.text, result))
        if result != None and len(result) > 0:
            element = toDoc.createElement("string")
            element.setAttribute("name", child.attrib["name"])
            textNode = toDoc.createTextNode(result)
            element.appendChild(textNode)
            toRoot.appendChild(element)
            index = index + 1
    print("正在写入文件...")
    if os.path.exists(dstfile):
        os.remove(dstfile)
    f = open(dstfile,'w')
    try :
        toDoc.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
        f.close()
    except:
        f.close()
        if os.path.exists(dstfile):
            os.remove(dstfile)
        f = open(dstfile,'wb')
        f.write(toDoc.toxml(encoding="utf-8"))
        f.close()
    print("写入文件完成...")

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

#后续可以读取xml，然后翻译之后，在写入xml