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

def calc_maxlen(all_language):
    max_len = 0
    for key in all_language.keys():
        if all_language[key] != None:
            ilen = len(all_language[key].split("|")[1])
            if ilen > max_len:
                max_len = ilen
    return max_len

def show_all_support_language():
    max_len = calc_maxlen(LANGUAGES)
    all_languages = sorted(LANGUAGES.keys())
    index = 1
    for item in all_languages:
        c = LANGUAGES[item].split("|")[1]
        leftspace = max_len - len(c)
        space = (2 * leftspace + 2) * " "
        print("%3d : %s%s%s" % (index, c, space, item))
        index += 1

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
        Log.out("")
    return None

def input_language():
    from_language = input_no("请输入源语言：")
    to_language = input_no("请输入目标语言：")
    if from_language == None or to_language == None:
        sys.exit(0)
    print("源语言：%s(%s) -> 目标语言 ：%s(%s)" % (LANGUAGES[from_language].split("|")[1] , from_language, LANGUAGES[to_language].split("|")[1] , to_language))
    return from_language, to_language

def translate_xml(from_language, to_language, xmlfile):
    if not os.path.exists(xmlfile):
        sys.exit(0)
    filedir = os.path.dirname(xmlfile)
    to_dir = "values-%s" % to_language
    dst_dir = os.path.join(filedir, to_dir)
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    print(dst_dir)
    doc = Document()  #创建DOM文档对象
    root = doc.createElement('resources') #创建根元素
    doc.appendChild(root)
    #return
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    children = list(root)
    for child in children:
        result = translate(child.text, from_language, to_language)
        print("%s -> %s" % (child.text, result))
        #print("%s" % child.attrib["name"])
        element = ET.Element("string", attrib={"name":child.attrib["name"]})
        element.text = result
        root.append(element)
    print("")
    for r in root:
        print("%s : %s" % (r.attrib["name"], r.text))
show_all_support_language()
from_language, to_language = input_language()
translate_xml(from_language, to_language, r"D:\temp\rpa_strings.xml")

#后续可以读取xml，然后翻译之后，在写入xml