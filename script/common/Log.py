#!/usr/bin/python
# coding: UTF-8

import sys
import os
DEBUG_LEVEL = ""
# 日志输出函数
def d(tag, msg):
    print(tag + " : %s" % msg)

def out(msg, show=True):
    if (show):
        print(msg)

def showNoReturn(msg):
    try:
        width = os.get_terminal_size().columns - 7
        sys.stdout.write(width * " " + '\r')
    except:
        pass
    sys.stdout.write(msg + '\r')
    sys.stdout.flush()
