#!/usr/bin/python
# coding: UTF-8

import sys
import os
DEBUG_LEVEL = ""

callback_writemsg = None
def setCallback(writemsg):
    global callback_writemsg
    callback_writemsg = writemsg
# 日志输出函数
def d(tag, msg):
    print(tag + " : %s" % msg)

def out(msg, show=True, end="\n"):
    if (callback_writemsg != None):
        callback_writemsg(msg)
        return
    if (show):
        try:
            print(msg, end=end)
        except:
            pass

def showNoReturn(msg):
    try:
        width = os.get_terminal_size().columns - 7
        sys.stdout.write(width * " " + '\r')
    except:
        pass
    sys.stdout.write(msg + '\r')
    sys.stdout.flush()
