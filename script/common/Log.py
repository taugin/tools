#!/usr/bin/python
# coding: UTF-8

import sys
DEBUG_LEVEL = ""
# 日志输出函数
def d(tag, msg):
    print(tag + " : %s" % msg)

def out(msg, show=True):
    if (show):
        print(msg)

def showNoReturn(msg):
    sys.stdout.write(msg + '\r')
    sys.stdout.flush()
