#!/usr/bin/python
# coding: UTF-8

DEBUG_LEVEL = ""
# 日志输出函数
def d(tag, msg):
    print(tag + " : %s" % msg)

def out(msg, show=True):
    if (show):
        print(msg)

