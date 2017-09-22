#!/usr/bin/python
# coding: UTF-8
# -*- coding: UTF-8 -*-
#python tkinter menu
#python version 3.3.2
#EN = Window 7


import os;
from tkinter import *
import tkinter.filedialog;
import tkinter.scrolledtext;
import tkinter.messagebox;
import subprocess;
import threading
import platform

INTERFACE_WIDTH = 1000
INTERFACE_HEIGHT = 800

def get_tk():
    '''获取一个Tk对象'''
    return Tk()

def set_tk_title(tk, title):
    '''给窗口定义title'''
    if title is not None and title != '':
        tk.title(title)
    else:
        tk.title('Hongten v1.0')

def set_tk_geometry(tk, size):
    '''设置窗口大小，size的格式为：widthxheight,如：size = '200x100'.'''
    if size is not None and size != '':
        tk.geometry(size)
    else:
        #tk.geometry('800x600')
        center_window(tk, INTERFACE_WIDTH, INTERFACE_HEIGHT)

def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2 - 40)
    root.geometry(size)

def onWindowClose(*e):
    bProcessing = False
    if (bProcessing):
        tkinter.messagebox.showwarning("警告", "程序正在处理中，请等待处理完毕")
    else:
        sys.exit(0)

class WinWidget:
    def __init__(self, tk):
        self.frame1 = Frame(tk, bg='red');
        self.frame1.pack(side='left', fill=BOTH)
        self.frame1["width"] = INTERFACE_WIDTH / 3
        self.frame1["height"] = INTERFACE_HEIGHT

        #应用frame
        self.frame2 = Frame(self.frame1);
        self.frame2.pack(side='left', fill=Y)
        self.frame2["width"] = INTERFACE_WIDTH / 3
        self.frame2["height"] = self.frame1["height"]

        cfgLabelHeight = 30
        self.cfgLabel = Label(self.frame2, text="应用配置")
        self.cfgLabel.place(width=self.frame2["width"] / 2, height = cfgLabelHeight)
        self.cfgAddBtn = Button(self.frame2, text="添加配置")
        self.cfgAddBtn.place(x= self.frame2["width"] / 2, width=self.frame2["width"] / 2, height = cfgLabelHeight)

        cfgBoxHeight = self.frame2["height"]/4
        scrollbar = Scrollbar(self.frame2)
        scrollbarWidth = int(scrollbar["width"])
        self.cfgBox = Listbox(self.frame2, yscrollcommand = scrollbar.set)
        self.cfgBox.place(y = cfgLabelHeight,width=self.frame2["width"] - scrollbarWidth, height = cfgBoxHeight)

        scrollbar.config(command = self.cfgBox.yview)
        scrollbar.place(x = self.frame2["width"] - scrollbarWidth, y = cfgLabelHeight, width=scrollbarWidth, height=cfgBoxHeight)

        #渠道frame总
        startx = 0
        starty = cfgBoxHeight + cfgLabelHeight
        btnw = 30
        btnh = 30
        channelBoxWidth = (self.frame1["width"] - btnw) / 2
        channelBoxHeight = (INTERFACE_HEIGHT - cfgLabelHeight - cfgBoxHeight) / 2

        scrollbar = Scrollbar(self.frame2)
        scrollbarWidth = int(scrollbar["width"])
        self.channelBoxTotal = Listbox(self.frame2, yscrollcommand = scrollbar.set)
        self.channelBoxTotal.place(x = startx, y = starty, width=channelBoxWidth - scrollbarWidth, height = channelBoxHeight)
        scrollbar.config(command = self.channelBoxTotal.yview)
        scrollbar.place(x = channelBoxWidth - scrollbarWidth, y = starty, width=scrollbarWidth, height=channelBoxHeight)

        startx = channelBoxWidth + btnw
        scrollbar = Scrollbar(self.frame2)
        scrollbarWidth = int(scrollbar["width"])
        self.channelBoxApp = Listbox(self.frame2, yscrollcommand = scrollbar.set)
        self.channelBoxApp.place(x = startx, y = starty, width=channelBoxWidth - scrollbarWidth, height = channelBoxHeight)
        scrollbar.config(command = self.channelBoxApp.yview)
        scrollbar.place(x = startx + channelBoxWidth - scrollbarWidth, y = starty, width=scrollbarWidth, height=channelBoxHeight)

        startx = channelBoxWidth
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight / 2 - btnh * 2
        label = Label(self.frame2, text='渠道')
        label.place(x = startx, y = starty, width=btnw, height=btnh)

        startx = channelBoxWidth
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight / 2 - btnh
        addBtn = Button(self.frame2, text='>>')
        addBtn.place(x = startx, y = starty, width=btnw, height=btnh)

        startx = channelBoxWidth
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight / 2
        subBtn = Button(self.frame2, text='<<')
        subBtn.place(x = startx, y = starty, width=btnw, height=btnh)

        #插件frame
        startx = 0
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight
        btnw = 30
        btnh = 30
        channelBoxWidth = (self.frame1["width"] - btnw) / 2
        channelBoxHeight = (INTERFACE_HEIGHT - cfgLabelHeight - cfgBoxHeight) / 2

        scrollbar = Scrollbar(self.frame2)
        scrollbarWidth = int(scrollbar["width"])
        self.channelBoxTotal = Listbox(self.frame2, yscrollcommand = scrollbar.set)
        self.channelBoxTotal.place(x = startx, y = starty, width=channelBoxWidth - scrollbarWidth, height = channelBoxHeight)
        scrollbar.config(command = self.channelBoxTotal.yview)
        scrollbar.place(x = channelBoxWidth - scrollbarWidth, y = starty, width=scrollbarWidth, height=channelBoxHeight)

        startx = channelBoxWidth + btnw
        scrollbar = Scrollbar(self.frame2)
        scrollbarWidth = int(scrollbar["width"])
        self.channelBoxApp = Listbox(self.frame2, yscrollcommand = scrollbar.set)
        self.channelBoxApp.place(x = startx, y = starty, width=channelBoxWidth - scrollbarWidth, height = channelBoxHeight)
        scrollbar.config(command = self.channelBoxApp.yview)
        scrollbar.place(x = startx + channelBoxWidth - scrollbarWidth, y = starty, width=scrollbarWidth, height=channelBoxHeight)

        startx = channelBoxWidth
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight / 2 - 2 * btnh + channelBoxHeight
        label = Label(self.frame2, text='插件')
        label.place(x = startx, y = starty, width=btnw, height=btnh)

        startx = channelBoxWidth
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight / 2 - btnh + channelBoxHeight
        addBtn = Button(self.frame2, text='>>')
        addBtn.place(x = startx, y = starty, width=btnw, height=btnh)

        startx = channelBoxWidth
        starty = cfgBoxHeight + cfgLabelHeight + channelBoxHeight / 2 + channelBoxHeight
        subBtn = Button(self.frame2, text='<<')
        subBtn.place(x = startx, y = starty, width=btnw, height=btnh)
        '''
        #渠道frame
        self.frame3 = Frame(self.frame1);
        self.frame3.grid(row=0, column=1)
        self.frame3["width"] = INTERFACE_WIDTH / 3
        self.frame3["height"] = self.frame1["height"]

        scrollbar = Scrollbar(self.frame3)
        scrollbarWidth = int(scrollbar["width"])
        self.channelBoxTotal = Listbox(self.frame3, yscrollcommand = scrollbar.set)
        self.channelBoxTotal.place(width=self.frame3["width"] - scrollbarWidth, height = self.frame3["height"])
        scrollbar.config(command = self.channelBoxTotal.yview)
        scrollbar.place(x = self.frame3["width"] - scrollbarWidth, width=scrollbarWidth, height=self.frame3["height"])

        #插件frame
        self.frame3 = Frame(self.frame1);
        self.frame3.grid(row=0, column=2)
        self.frame3["width"] = INTERFACE_WIDTH / 3
        self.frame3["height"] = self.frame1["height"]

        scrollbar = Scrollbar(self.frame3)
        scrollbarWidth = int(scrollbar["width"])
        self.pluginBox = Listbox(self.frame3, yscrollcommand = scrollbar.set)
        self.pluginBox.place(width=self.frame3["width"] - scrollbarWidth, height = self.frame3["height"])
        scrollbar.config(command = self.pluginBox.yview)
        scrollbar.place(x = self.frame3["width"] - scrollbarWidth, width=scrollbarWidth, height=self.frame3["height"])

        #下方frame
        self.frame4 = Frame(tk, bg='#ccc', bd=2);
        self.frame4.pack(fill=BOTH, expand=YES)
        '''
    def addWidget(self, tk):
        '''添加界面元素'''
        for c in range(100):
            self.cfgBox.insert(0, "ApkDemo%4s" % c);
        '''
        for c in range(100):
            self.channelBoxTotal.insert(0, "Channel%4s" % c);
        for c in range(100):
            self.pluginBox.insert(0, "Plugins%4s" % c);
        '''
        pass
root = get_tk()
#设置窗口大小
set_tk_geometry(root, '')
#设置窗口title
set_tk_title(root, 'APK打包工具')

#禁止缩放
root.resizable(width=False, height=False)

winWidget = WinWidget(root);
winWidget.addWidget(root)

root.protocol("WM_DELETE_WINDOW", onWindowClose)

mainloop()