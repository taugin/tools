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

__author__ = 'Hongten'
MODAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "../base/modapk.py")
MODAPK_FILE = os.path.normpath(MODAPK_FILE);
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

def fileSelect():
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
    winWidget.entrySrcVar.set(filename);

def thread_function(p):
    while True:
        line = p.stdout.readline()
        #print(line);
        if not line:
            break;
        winWidget.msgOutput.insert(END, line.decode(getEncoding()));
    winWidget.msgOutput.insert(END, "\n");
    global bProcessing;
    bProcessing = False;

def startModApk():
    winWidget.msgOutput.delete(0.0, END);
    srcApkPath = winWidget.entrySrc.get();
    newPkgName = winWidget.entryPkg.get();
    newLabelName = winWidget.entryTitle.get();
    reinforce = False;
    onlyDecompile = False;
    value = winWidget.loaderVarValue.get();
    if (value == 1): reinforce = True;
    else: reinforce = False;
    value = winWidget.onlyDecompileVarValue.get();
    if (value == 1): onlyDecompile = True;
    else: onlyDecompile = False;

    if (srcApkPath == None or srcApkPath == ""):
        tkinter.messagebox.showerror(title="错误", message="缺少源文件");
        return;

    debugText = "";
    debugText += "[Logging...] 源 A P K : %s\n" % srcApkPath;
    debugText += "[Logging...] 新 包 名 : %s\n" % newPkgName;
    debugText += "[Logging...] 新应用名 : %s\n" % newLabelName;
    debugText += "[Logging...] 是否加壳 : %s\n" % reinforce;
    winWidget.msgOutput.insert(END, debugText);
    cmdlist = [];
    cmdlist.append("python");
    cmdlist.append("-u");
    cmdlist.append(MODAPK_FILE);
    if (newPkgName != None and newPkgName != ""):
        cmdlist.append("-p");
        cmdlist.append(newPkgName);
    if (newLabelName != None and newLabelName != ""):
        cmdlist.append("-l");
        cmdlist.append(newLabelName);
    if (reinforce):
        cmdlist.append("-e");
    if (onlyDecompile):
        cmdlist.append("-d");
    cmdlist.append("-g");
    cmdlist.append(srcApkPath);
    winWidget.msgOutput.insert(END, "[Logging...] " + " ".join(cmdlist));
    winWidget.msgOutput.insert(END, "\n");
    process = subprocess.Popen(cmdlist, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
    global bProcessing;
    bProcessing = True;
    t = threading.Thread(target=thread_function, args=(process,));
    t.start();

class WinWidget:
    def __init__(self, tk):
        self.frame1 = Frame(tk, bg='gray');
        #self.frame1["width"] = 50
        self.frame1.pack(fill=X);

        self.entrySrcVar = StringVar();
        self.entrySrc = Entry(self.frame1, width="90", textvariable=self.entrySrcVar);
        self.entrySrc['state'] = 'readonly'
        #self.entrySrc.bind("<KeyPress>", lambda e:"break") # 只读

        self.entryPkg = Entry(self.frame1, width="90");

        self.entryTitle = Entry(self.frame1, width="90");

        self.checkFrame = Frame(self.frame1, bg='gray');
        self.loaderVarValue = IntVar();
        self.loaderEncryptCheck = Checkbutton(self.checkFrame, text="加壳", variable = self.loaderVarValue, bg='gray');

        self.onlyDecompileVarValue = IntVar();
        self.onlyDecompileEncrypt = Checkbutton(self.checkFrame, text="仅反编译", variable = self.onlyDecompileVarValue, bg='gray');

        self.msgOutput = tkinter.scrolledtext.ScrolledText(tk, bg='white', relief=SUNKEN);
        self.msgOutput.bind("<KeyPress>", lambda e:"break") # 只读

    def addWidget(self, tk):
        '''添加界面元素'''
        labelSrc = Label(self.frame1, text="源文件");
        labelSrc.grid(row=0, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.entrySrc.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5);
        buttonFileDlg = Button(self.frame1, text='选择', command=fileSelect, width="10");
        buttonFileDlg.grid(row=0, column=2, padx=5);

        labekPkg = Label(self.frame1, text="新包名");
        labekPkg.grid(row=1, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.entryPkg.grid(row=1, column=1, padx=5, pady=5, ipadx=5, ipady=5);
        
        labelTitle = Label(self.frame1, text="新标题");
        labelTitle.grid(row=2, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.entryTitle.grid(row=2, column=1, padx=5, pady=5, ipadx=5, ipady=5);

        labelEncrypt = Label(self.frame1, text="选   项");
        labelEncrypt.grid(row=3, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.checkFrame.grid(row=3, column=1, padx=5, pady=5, sticky='w');
        self.loaderEncryptCheck.pack(side=LEFT);
        self.onlyDecompileEncrypt.pack(padx=10);
    
        buttonStart = Button(self.frame1, text="开  始", command=startModApk);
        #buttonStart['width'] = 20;
        buttonStart.grid(row=4, padx=5, pady=5, columnspan=3, sticky='w', ipadx=3, ipady=0);

        self.msgOutput.pack(fill=BOTH, side=LEFT, expand=True, pady=5);

#获得窗口对象
root = get_tk()
#设置窗口大小
set_tk_geometry(root, '')
#设置窗口title
set_tk_title(root, 'APK修改工具')

#禁止缩放
root.resizable(width=False, height=False)

winWidget = WinWidget(root);
winWidget.addWidget(root)

root.protocol("WM_DELETE_WINDOW", onWindowClose)

mainloop()