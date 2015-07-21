#!/usr/bin/python
# coding: UTF-8

import tkinter
import subprocess

pressing = False
TRACKING_ID = 0

EV_DEVICE = "/dev/input/event0"
ABS_MT_POSITION_X = "%d" % int(eval("0x35"))
ABS_MT_POSITION_Y = "%d" % int(eval("0x36"))

ABS_MT_TRACKING_ID = "%d" % int(eval("0x39"))
EV_ABS = "%d" % int(eval("0x3"))
EV_SYN = "%d" % int(eval("0x0"))
SYN_REPORT = "%d" % int(eval("0x0"))

def log(str, show=True):
    if (show):
        #top.title(str)
        print(str)

class PhoneEvent:
    def __init__(self, device, type, code, value):
        self.device = device;
        self.type = type;
        self.code = code;
        self.value = value;

def sendevent(phoneevent):
    cmdlist = ["adb", "shell", "sendevent", phoneevent.device, phoneevent.type, phoneevent.code, phoneevent.value]
    log(" ".join(cmdlist))
    subprocess.call(cmdlist)

def mousenevent(event):
    #log("[Move] x : %d, y : %d" % (event.x, event.y))
    if (pressing):
        phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_POSITION_X, "%d" % event.x)
        sendevent(phoneevent)
        phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_POSITION_Y, "%d" % event.y)
        sendevent(phoneevent)

        phoneevent = PhoneEvent(EV_DEVICE, EV_SYN, SYN_REPORT, "0")
        sendevent(phoneevent)

def mouseclick(event):
    log("[Click] x : %d, y : %d, state : %d" % (event.x, event.y, event.state))

def mouse_left_down(event):
    global pressing
    global TRACKING_ID
    TRACKING_ID = TRACKING_ID + 1
    
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_TRACKING_ID, "%d" % TRACKING_ID)
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_POSITION_X, "%d" % event.x)
    sendevent(phoneevent)
    phoneevent = PhoneEvent(EV_DEVICE, EV_ABS, ABS_MT_POSITION_Y, "%d" % event.y)
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


class CommonSocket:
    pass

top = tkinter.Tk()
top.resizable(False,False)
top.geometry('540x960+100+5')
top.bind("<Motion>", mousenevent)
top.bind("<Button-1>", mouseclick)
top.bind("<ButtonPress-1>", mouse_left_down)
top.bind("<ButtonRelease-1>", mouse_left_up)
top.mainloop()

