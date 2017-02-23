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

'''
    在python 3.3.2中，tkinter模块可以创建一个窗口控件，如Java中的Swing
    功能描述：
        根据Python 3.3.2 IDEL的菜单，创建出一个tkinter窗口
        File-Exit    :  退出功能完成
        Help-About IDEL     ： 打印相应信息
        其他的菜单项，当点击时，会打印出相应菜单项的名称
'''

__author__ = 'Hongten'
MODAPK_FILE = os.path.join(os.path.dirname(sys.argv[0]), "../base/modapk.py")
MODAPK_FILE = os.path.normpath(MODAPK_FILE);

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


def fileSelect():
    '''apk文件选择'''
    if (platform.system().lower() == "windows" and False):
        import win32ui
        dlg = win32ui.CreateFileDialog(1) # 1表示打开文件对话框
        dlg.SetOFNInitialDir('E:\\') # 设置打开文件对话框中的初始显示目录
        dlg.DoModal()
        filename = dlg.GetPathName() # 获取选择的文件名称
    else:
        #fd = tkinter.filedialog.LoadFileDialog(root) # 创建打开文件对话框
        #filename = fd.go() # 显示打开文件对话框，并获取选择的文件名称
        fd = tkinter.filedialog.askopenfile(filetypes=[("text file", "*.apk"), ("all", "*.*")], )
        if (fd != None):
            filename = fd.name;
            if (filename != None):
                filename = os.path.normpath(filename);
    winWidget.entrySrcVar.set(filename);

def callCheckbutton():
    value = winWidget.checkVarValue.get();
    if (value == 1):
        winWidget.checkVar.set("开启加壳");
    else:
        winWidget.checkVar.set("关闭加壳");

def thread_function(p):
    while True:
        line = p.stdout.readline()
        #print(line);
        if not line:
            break;
        winWidget.msgOutput.insert(END, line);
    winWidget.msgOutput.insert(END, "\n");

def startModApk():
    winWidget.msgOutput.delete(0.0, END);
    srcApkPath = winWidget.entrySrc.get();
    newPkgName = winWidget.entryPkg.get();
    newLabelName = winWidget.entryTitle.get();
    reinforce = False;
    value = winWidget.checkVarValue.get();
    if (value == 1):
        reinforce = True;
    else:
        reinforce = False;

    if (srcApkPath == None or srcApkPath == ""):
        tkinter.messagebox.showerror(title="错误", message="缺少源文件");
        return;

    debugText = "源 A P K : %s\n新 包 名 : %s\n新应用名 : %s\n是否加壳 : %s\n" % (srcApkPath, newPkgName, newLabelName, reinforce);
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
    cmdlist.append(srcApkPath);
    winWidget.msgOutput.insert(END, "[Logging...] " + " ".join(cmdlist));
    winWidget.msgOutput.insert(END, "\n");
    process = subprocess.Popen(cmdlist, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
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

        self.checkVar = StringVar();
        self.checkVar.set("关闭加壳")
        self.checkVarValue = IntVar();
        self.checkEncrypt = Checkbutton(self.frame1, textvariable = self.checkVar, variable = self.checkVarValue, bg='gray', command = callCheckbutton);

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

        labelEncrypt = Label(self.frame1, text="加   壳");
        labelEncrypt.grid(row=3, column=0, padx=5, pady=5, ipadx=3, ipady=3);
        self.checkEncrypt.grid(row=3, column=1, padx=5, pady=5, sticky='w');
    
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

mainloop()