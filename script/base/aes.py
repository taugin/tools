#!/usr/bin/python
# coding: UTF-8
import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import Common
import Log

import getopt
import subprocess

ENCRYPT = True
BINARY = False

def encrypt_file(key, input_file, output_file):
    global BINARY
    if input_file == None or not os.path.exists(input_file):
        usage()
        return False
    input_file = os.path.abspath(input_file)
    if output_file == None or output_file.strip() == "":
        basename = os.path.basename(input_file)
        name, ext= os.path.splitext(basename)
        output_file = "%s-encrypt%s" % (name, ext)
        output_file = os.path.abspath(output_file)
    else:
        output_file = os.path.abspath(output_file)
    if key == None or len(key) <= 0:
        key = "123456789"
    Log.out("\n[Logging...] 加密文件 key : [%s], binary : [%s], input : [%s], output : [%s]\n" % (key, BINARY, input_file, output_file))
    cmdlist = []
    cmdlist.append(Common.JAVA())
    cmdlist.append("-jar")
    cmdlist.append(Common.AES_JAR)
    cmdlist.append("-e")
    if BINARY:
        cmdlist.append("-b")
    cmdlist.append("-k")
    cmdlist.append(key)
    cmdlist.append("-i")
    cmdlist.append(input_file)
    cmdlist.append("-o")
    cmdlist.append(output_file)
    subprocess.call(cmdlist)

def decrypt_file(key, input_file, output_file):
    global BINARY
    if input_file == None or not os.path.exists(input_file):
        usage()
        sys.exit(-1)
    input_file = os.path.abspath(input_file)
    if output_file == None or output_file.strip() == "":
        basename = os.path.basename(input_file)
        name, ext= os.path.splitext(basename)
        output_file = "%s-decrypt%s" % (name, ext)
        output_file = os.path.abspath(output_file)
    else:
        output_file = os.path.abspath(output_file)
    if key == None or len(key) <= 0:
        key = "123456789"
    Log.out("\n[Logging] 解密文件 key : [%s], binary : [%s], input : [%s], output : [%s]\n" % (key, BINARY, input_file, output_file))
    cmdlist = []
    cmdlist.append(Common.JAVA())
    cmdlist.append("-jar")
    cmdlist.append(Common.AES_JAR)
    cmdlist.append("-d")
    if BINARY:
        cmdlist.append("-b")
    cmdlist.append("-k")
    cmdlist.append(key)
    cmdlist.append("-i")
    cmdlist.append(input_file)
    cmdlist.append("-o")
    cmdlist.append(output_file)
    subprocess.call(cmdlist)
    
def encrypt_string(key, input_string):
    if input_string == None or len(input_string) <= 0:
        usage()
        return False
    if key == None or len(key) <= 0:
        key = "123456"
    Log.out("\n[Logging...] 加密字符串 key : [%s], input : [%s]\n" % (key, input_string))
    cmdlist = [Common.JAVA(), "-jar", Common.AES_JAR, "-e", "-k", key, "-s", input_string]
    subprocess.call(cmdlist)
    Log.out("")

def decrypt_string(key, input_string):
    if input_string == None or len(input_string) <= 0:
        usage()
        return False
    if key == None or len(key) <= 0:
        key = "123456"
    Log.out("\n[Logging] 解密字符串 key : [%s], input : [%s]\n" % (key, input_string))
    cmdlist = [Common.JAVA(), "-jar", Common.AES_JAR, "-d", "-k", key, "-s", input_string]
    subprocess.call(cmdlist)
    Log.out("")
# start ============================================================================================
def usage():
    Log.out("[Logging...] 脚本缺少参数 : %s -e/-d -k 123456 [-i inputfile -o outputfile]/[-s string]" % os.path.basename(sys.argv[0]), True);

if (len(sys.argv) < 4):
    usage()
    sys.exit()
input_string = None
input_file = None
output_file = None
key = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "s:k:i:o:edb")
    for op, value in opts:
        if (op == "-k"):
            key = value
        elif (op == "-i") :
            input_file = value
        elif (op == "-o") :
            output_file = value
        elif (op == "-e") :
            ENCRYPT = True
        elif (op == "-d") :
            ENCRYPT = False
        elif (op == "-s"):
            input_string = value
        elif (op == "-b"):
            BINARY = True
except getopt.GetoptError as err:
    Log.out(err)
    sys.exit()
if input_string != None and len(input_string) > 0:
    if ENCRYPT:
        encrypt_string(key, input_string)
    else:
        decrypt_string(key, input_string)
else:
    if ENCRYPT:
        encrypt_file(key, input_file, output_file)
    else:
        decrypt_file(key, input_file, output_file)
Common.pause()