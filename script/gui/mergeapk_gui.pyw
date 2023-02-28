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
import platform;
import sys
import signal

import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "merger")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)
import mergeapk

DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import Log

bProcessing = False;

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
        center_window(tk, 800, 600)

def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2 - 40)
    root.geometry(size) 

def getEncoding():
    if sys.stdout == None:
        return "gbk";
    if sys.stdout.encoding == None:
        return "gbk";
    if (sys.stdout.encoding.lower() == "utf-8"):
        return "utf-8";
    return "gbk";

def onWindowClose(*e):
    global bProcessing;
    if (bProcessing):
        tkinter.messagebox.showwarning("警告", "程序正在处理中，请等待处理完毕")
    else:
        sys.exit(0)

def fileSelectMaster():
    '''apk文件选择'''
    filename = "";
    if (platform.system().lower() == "windows" and False):
        #import win32ui
        #dlg = win32ui.CreateFileDialog(1) # 1表示打开文件对话框
        #dlg.SetOFNInitialDir('E:\\') # 设置打开文件对话框中的初始显示目录
        #dlg.DoModal()
        #filename = dlg.GetPathName() # 获取选择的文件名称
        pass
    else:
        #fd = tkinter.filedialog.LoadFileDialog(root) # 创建打开文件对话框
        #filename = fd.go() # 显示打开文件对话框，并获取选择的文件名称
        fd = tkinter.filedialog.askopenfile(filetypes=[("text file", "*.apk"), ("all", "*.*")], )
        if (fd != None):
            filename = fd.name;
            if (filename != None):
                filename = os.path.normpath(filename);
    winWidget.entryMasterVar.set(filename);

def fileSelectSlave():
    '''apk文件选择'''
    filename = "";
    if (platform.system().lower() == "windows" and False):
        #import win32ui
        #dlg = win32ui.CreateFileDialog(1) # 1表示打开文件对话框
        #dlg.SetOFNInitialDir('E:\\') # 设置打开文件对话框中的初始显示目录
        #dlg.DoModal()
        #filename = dlg.GetPathName() # 获取选择的文件名称
        pass
    else:
        #fd = tkinter.filedialog.LoadFileDialog(root) # 创建打开文件对话框
        #filename = fd.go() # 显示打开文件对话框，并获取选择的文件名称
        fd = tkinter.filedialog.askopenfile(filetypes=[("text file", "*.apk"), ("all", "*.*")], )
        if (fd != None):
            filename = fd.name;
            if (filename != None):
                filename = os.path.normpath(filename);
    winWidget.entrySlaveVar.set(filename);

def callback(msg):
    winWidget.msgOutput.insert(END, msg);
    winWidget.msgOutput.insert(END, "\n");

def thread_function(masterApk, slaveApk, debugmode, formatOutput):
    global bProcessing;
    Log.setCallback(callback)
    mergeapk.mergeapk_byargs(masterApk, slaveApk, debugmode, formatOutput)
    bProcessing = False;

def startMergeApk():
    global bProcessing
    masterApk = winWidget.entryMaster.get();
    slaveApk = winWidget.entrySlave.get();
    formatOutput = winWidget.entryTitle.get();
    debugmode = False;
    value = winWidget.debugModeValue.get();
    if (value == 1): debugmode = True;
    else: debugmode = False;

    if (masterApk == None or masterApk == ""):
        tkinter.messagebox.showerror(title="错误", message="缺少主文件");
        return;
    if (slaveApk == None or slaveApk == ""):
        tkinter.messagebox.showerror(title="错误", message="缺少从文件");
        return;
    if bProcessing == True:
        tkinter.messagebox.showwarning("警告", "程序正在运行");
        return
        
    #开始处理文件合并
    bProcessing = True
    winWidget.msgOutput.delete(0.0, END);
    debugText = "";
    debugText += "[Logging...] 主文件 : %s\n" % masterApk;
    debugText += "[Logging...] 从文件 : %s\n" % slaveApk;
    #debugText += "[Logging...] 格式化 : %s\n" % formatOutput;
    if debugmode == True:
        debugText += "[Logging...] 调  试 : 开启";
    else:
        debugText += "[Logging...] 调  试 : 关闭";
    winWidget.msgOutput.insert(END, debugText);
    winWidget.msgOutput.insert(END, "\n");
    t = threading.Thread(target=thread_function, args=(masterApk, slaveApk, debugmode,formatOutput,));
    t.start();

class WinWidget:
    def __init__(self, tk):
        self.frame1 = Frame(tk, bg='gray');
        #self.frame1["width"] = 50
        self.frame1.pack(fill=X);

        self.entryMasterVar = StringVar();
        self.entryMaster = Entry(self.frame1, width="90", textvariable=self.entryMasterVar);
        self.entryMaster['state'] = 'readonly'
        #self.entryMaster.bind("<KeyPress>", lambda e:"break") # 只读

        self.entrySlaveVar = StringVar();
        self.entrySlave = Entry(self.frame1, width="90", textvariable=self.entrySlaveVar);
        self.entrySlave['state'] = 'readonly'
        #self.entryMaster.bind("<KeyPress>", lambda e:"break") # 只读

        self.entryTitleVar = StringVar();
        self.entryTitleVar.set("{apklabel}_Release_v{vername}_{vercode}_{datetime}.apk")
        self.entryTitle = Entry(self.frame1, width="90", textvariable=self.entryTitleVar);
        self.entryTitle['state'] = 'readonly'

        self.checkFrame = Frame(self.frame1, bg='gray');
        self.debugModeValue = IntVar();
        self.checkDebugMode = Checkbutton(self.checkFrame, text="调试模式", variable = self.debugModeValue, bg='gray');

        self.msgOutput = tkinter.scrolledtext.ScrolledText(tk, bg='white', relief=SUNKEN);
        self.msgOutput.bind("<KeyPress>", lambda e:"break") # 只读

    def addWidget(self, tk):
        '''添加界面元素'''
        labelMaster = Label(self.frame1, text="主文件");
        labelMaster.grid(row=0, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.entryMaster.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5);
        buttonFileDlgMaster = Button(self.frame1, text='选择', command=fileSelectMaster, width="10");
        buttonFileDlgMaster.grid(row=0, column=2, padx=5);

        labelSlave = Label(self.frame1, text="从文件");
        labelSlave.grid(row=1, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.entrySlave.grid(row=1, column=1, padx=5, pady=5, ipadx=5, ipady=5);
        buttonFileDlgSlave = Button(self.frame1, text='选择', command=fileSelectSlave, width="10");
        buttonFileDlgSlave.grid(row=1, column=2, padx=5);
        
        #labelTitle = Label(self.frame1, text="格式化");
        #labelTitle.grid(row=2, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        #self.entryTitle.grid(row=2, column=1, padx=5, pady=5, ipadx=5, ipady=5);

        labelEncrypt = Label(self.frame1, text="选   项");
        labelEncrypt.grid(row=3, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.checkFrame.grid(row=3, column=1, padx=5, pady=5, sticky='w');
        self.checkDebugMode.pack(side=LEFT);
    
        buttonStart = Button(self.frame1, text="开  始", command=startMergeApk);
        #buttonStart['width'] = 20;
        buttonStart.grid(row=4, padx=5, pady=5, columnspan=3, sticky='w', ipadx=3, ipady=0);

        self.msgOutput.pack(fill=BOTH, side=LEFT, expand=True, pady=5);

#获得窗口对象
root = get_tk()
#设置窗口大小
#set_tk_geometry(root, '')
#设置窗口title
set_tk_title(root, 'APK合并工具')

#禁止缩放
root.resizable(width=False, height=False)

winWidget = WinWidget(root);
winWidget.addWidget(root)

root.protocol("WM_DELETE_WINDOW", onWindowClose)

mainloop()
