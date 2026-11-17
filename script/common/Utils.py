#!/usr/bin/python
# coding: UTF-8

from copy import deepcopy
import os
import sys
import shutil
import platform
import PathCompat
import Log

def pause(str="[Logging...] 按任意键退出"):
    if (platform.system().lower() == "windows"):
        import msvcrt
        print(str)
        msvcrt.getch()
    else:
        input(str)

def copydir(fromdir, todir, override = True):
    mylist = PathCompat.walk(fromdir, True)
    for root, filedir, files in mylist:
        for file in files:
            todirname = os.path.join(todir, os.path.relpath(root, fromdir))
            if (os.path.exists(PathCompat.fsPath(todirname)) == False):
                os.makedirs(PathCompat.fsPath(todirname))
            #sdk文件夹内的文件
            fromdirfile = os.path.join(root, file)
            todirfile = os.path.join(todirname, file)
            copyfile(fromdirfile, todirfile, override)

def copyfile(fromfile, tofile, override = True):
    try:
        dirname = os.path.dirname(tofile) or os.curdir
        if (not os.path.exists(PathCompat.fsPath(dirname))):
            os.makedirs(PathCompat.fsPath(dirname))
        if override == False:
            if (os.path.exists(PathCompat.fsPath(tofile))):
                return
        shutil.copy2(PathCompat.fsPath(fromfile), PathCompat.fsPath(tofile))
    except Exception as e:
        print("Exception : copyfile %s -> %s : %s" % (fromfile, tofile, e))

def deletedir(path):
    try:
        path = PathCompat.fsPath(path)
        if not os.path.lexists(path):
            return
        shutil.rmtree(path)
    except Exception as e:
        print("Exception : %s" % e)

def movefile(fromfile, tofile):
    try:
        dirname = os.path.dirname(tofile) or os.curdir
        if (not os.path.exists(PathCompat.fsPath(dirname))):
            os.makedirs(PathCompat.fsPath(dirname))
        shutil.move(PathCompat.fsPath(fromfile), PathCompat.fsPath(tofile))
        deleteEmptyDir(fromfile)
    except Exception as e:
        print("Exception : movefile %s -> %s : %s" % (fromfile, tofile, e))

def deleteEmptyDir(path):
    try:
        while True:
            dirname = os.path.dirname(path)
            os.rmdir(PathCompat.fsPath(dirname))
            path = dirname
    except:
        pass

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

#安全获取字典的值
def getvalue(item, key):
    try:
        return item[key]
    except:
        return None

#获取xml的节点属性
def getattrib(item, key):
    try:
        return item.attrib[key];
    except:
        return None

#规范化路径名称
def normalPath(path):
    return os.path.normpath(path)

def exitOnFalse(ret):
    if (ret == False):
        sys.exit()

def isEmpty(string):
    if (string == None or string.strip() == ""):
        return True
    return False

def list_files(dirname):
    allFiles = []
    mylist = PathCompat.walk(dirname, True)
    for root, filedir, files in mylist:
        for file in files:
            allFiles.append(os.path.normpath(os.path.join(root, file)))
    return allFiles

def deleteFile(file):
    if (os.path.exists(PathCompat.fsPath(file))):
        os.remove(PathCompat.fsPath(file))

def parseString(line):
    format_code = ["utf8", "gbk", "gb2312"]
    result = ""
    for f in format_code:
        try:
            result = line.decode(f, "ignore")
            return result
        except:
            pass
    return result or ""

def printExecCmdString(cmdlist):
    cmdlist_deepcopy = deepcopy(cmdlist)
    cmdlist_deepcopy[0] = os.path.basename(cmdlist_deepcopy[0])
    Log.out("[Logging...] 执行程序 : [{}]".format(' '.join(cmdlist_deepcopy)))
