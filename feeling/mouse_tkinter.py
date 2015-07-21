#!/usr/bin/python
# coding: UTF-8

import sys
import threading
import tkinter
import socket
import subprocess


#事件定义
TRACKING_ID = 0
EV_DEVICE = "/dev/input/event0"
ABS_MT_POSITION_X = "%d" % int(eval("0x35"))
ABS_MT_POSITION_Y = "%d" % int(eval("0x36"))

ABS_MT_TRACKING_ID = "%d" % int(eval("0x39"))
EV_ABS = "%d" % int(eval("0x3"))

EV_KEY = "%d" % int(eval("0x1"))
KEY_BACK = "%d" % int(eval("0x9e"))
KEY_HOMEPAGE = "%d" % int(eval("0xac"))

DOWN = "%d" % int(eval("0x1"))
UP = "%d" % int(eval("0x0"))

EV_SYN = "%d" % int(eval("0x0"))
SYN_REPORT = "%d" % int(eval("0x0"))

pressing = False
SCREEN_ORIENTATION = 0
if (len(sys.argv) > 1):
    SCREEN_ORIENTATION = 1

def log(str, show=True):
    if (show):
        #top.title(str)
        print(str)

def getgeometry():
    w = 0
    h = 0
    if (SCREEN_ORIENTATION == 0):
        w = 540
        h = 960
    else:
        w = 960
        h = 540
    ws = top.winfo_screenwidth()  
    hs = top.winfo_screenheight()  
    # calculate position x, y  
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    geometry = '%dx%d+%d+%d' % (w, h, x, y)
    return geometry

def recvfrom():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_addr = ("127.0.0.1", 8988)
        s.bind(host_addr)
        log("waiting for data from phone ...")
        data, (addr, port) = s.recvfrom(1024)
        log("addr : " + addr)

class CommonSocket:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.connect(("10.0.1.114", 8989))
        log("启动线程")
        th = threading.Thread(target=recvfrom, args=())
        #th.start()
    def senddata(self, data):
        self.s.sendall(data.encode("utf-8"))

class ScreenTranform:
    def __init__(self):
        pass

    def getpositionx(self):
        if (SCREEN_ORIENTATION == 0):
            return ABS_MT_POSITION_X
        return ABS_MT_POSITION_Y

    def getpositiony(self):
        if (SCREEN_ORIENTATION == 0):
            return ABS_MT_POSITION_Y
        return ABS_MT_POSITION_X

    def process_position(self, event):
        if (event.code == self.getpositiony() and SCREEN_ORIENTATION != 0):
            tmp = int(event.value)
            tmp = 540-tmp
            event.value = "%d" % tmp

class PhoneEvent:
    def __init__(self, device, type, code, value):
        self.device = device;
        self.type = type;
        self.code = code;
        self.value = value;
        screenTransform.process_position(self)

def sendevent(phoneevent):
    cmdlist = ["adb", "shell", "sendevent", phoneevent.device, phoneevent.type, phoneevent.code, phoneevent.value]
    log(" ".join(cmdlist))
    subprocess.call(cmdlist)

def mousenevent(event):
    #log("[Move] x : %d, y : %d" % (event.x, event.y))
    data = {"x":event.x, "y":event.y}
    udpsocket.senddata(str(data))
    if (pressing):
        phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, screenTransform.getpositionx(), "%d" % event.x)
        sendevent(phoneevent)
        phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, screenTransform.getpositiony(), "%d" % event.y)
        sendevent(phoneevent)

        phoneevent = PhoneEvent(EV_DEVICE, EV_SYN, SYN_REPORT, "0")
        sendevent(phoneevent)

def mouse_left_down(event):
    global pressing
    global TRACKING_ID
    TRACKING_ID = TRACKING_ID + 1
    
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_TRACKING_ID, "%d" % TRACKING_ID)
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, screenTransform.getpositionx(), "%d" % event.x)
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, screenTransform.getpositiony(), "%d" % event.y)
    sendevent(phoneevent)
    
    phoneevent = PhoneEvent(EV_DEVICE, EV_SYN, SYN_REPORT, "0")
    sendevent(phoneevent)

    pressing = True

def mouse_left_up(event):
    global pressing
    #log("[Up] x : %d, y : %d, state : %d" % (event.x, event.y, event.state))
    pressing = False
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_TRACKING_ID, "-1")
    sendevent(phoneevent)

    phoneevent = PhoneEvent(EV_DEVICE, EV_SYN, SYN_REPORT, "0")
    sendevent(phoneevent)

def process_click(key):
    phoneevent = PhoneEvent(EV_DEVICE, EV_KEY, key, DOWN)
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_SYN, SYN_REPORT, "0")
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_KEY, key, UP)
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_SYN, SYN_REPORT, "0")
    sendevent(phoneevent)

def mouse_right_click(event):
    process_click(KEY_BACK)

def mouse_middle_click(event):
    process_click(KEY_HOMEPAGE)

def f2_click(event):
    global pressing
    if (pressing):
        pressing = False
    else:
        pressing = True
    log("pressing : [%d]" % pressing)

def f12_click(event):
    global SCREEN_ORIENTATION
    if (SCREEN_ORIENTATION == 0):
        SCREEN_ORIENTATION = 1
    else:
        SCREEN_ORIENTATION = 0
    top.geometry(getgeometry())

def esc_click(event):
    top.quit()

udpsocket = CommonSocket()
screenTransform = ScreenTranform()

top = tkinter.Tk()
top.resizable(False,False)
top.geometry(getgeometry())
top.bind("<Motion>", mousenevent)
top.bind("<ButtonPress-1>", mouse_left_down)
top.bind("<ButtonRelease-1>", mouse_left_up)
top.bind("<Button-2>", mouse_middle_click)
top.bind("<Button-3>", mouse_right_click)
top.bind("<Key-F2>", f2_click)
top.bind("<Key-F12>", f12_click)
top.bind("<Key-Escape>", esc_click)

top.mainloop()

