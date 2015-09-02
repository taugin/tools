#!/usr/bin/python
# coding: UTF-8

import sys
import threading
from tkinter import *
import socket
import time
import subprocess

def log(str, show=True):
    if (show):
        print(str)

def getgeometry():
    w = 600
    h = 800
    ws = top.winfo_screenwidth()  
    hs = top.winfo_screenheight() - 100
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    geometry = '%dx%d+%d+%d' % (w, h, x, y + 10)
    return geometry

def sendevent(code):
    #log("code : %d" % code)
    cmdlist = ["adb", "shell", "input", "keyevent", "%d" % code]
    subprocess.call(cmdlist, shell=True)

top = Tk()

up = Button(top, text="向上", width="10", height="5", command=lambda:sendevent(19)).grid(row=0, column=1)

down = Button(top, text="向下", width="10", height="5", command=lambda:sendevent(20)).grid(row=2, column=1)

left = Button(top, text="向左", width="10", height="5", command=lambda:sendevent(21)).grid(row=1, column=0)

right = Button(top, text="向右", width="10", height="5", command=lambda:sendevent(22)).grid(row=1, column=2)

ok = Button(top, text="确定", width="10", height="5", command=lambda:sendevent(23)).grid(row=1, column=1)

menu = Button(top, text="菜单", width="10", height="5", command=lambda:sendevent(82)).grid(row=3, column=0)

back = Button(top, text="返回", width="10", height="5", command=lambda:sendevent(4)).grid(row=3, column=2)

top.bind("<KeyPress-Up>", lambda event:sendevent(19))
top.bind("<KeyPress-Down>", lambda event:sendevent(20))
top.bind("<KeyPress-Left>", lambda event:sendevent(21))
top.bind("<KeyPress-Right>", lambda event:sendevent(22))
top.bind("<KeyPress-Return>", lambda event:sendevent(23))
top.bind("<Key-Escape>", lambda event:top.quit())
top.resizable(False,False)
top.geometry(getgeometry())
top.mainloop()
log("quit")
