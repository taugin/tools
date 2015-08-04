#!/usr/bin/python
# coding: UTF-8

import sys
import threading
import tkinter
import socket
import time
import subprocess


#事件定义
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRACKING_ID = 1000
EV_TOUCH_DEVICE = "/dev/input/event0"

ABS_MT_SLOT = "%d" % int(eval("0x2f"))

ABS_MT_POSITION_X = "%d" % int(eval("0x35"))
ABS_MT_POSITION_Y = "%d" % int(eval("0x36"))

ABS_MT_TRACKING_ID = "%d" % int(eval("0x39"))
ABS_MT_PRESSURE = "%d" % int(eval("0x3a"))
ABS_MT_TOUCH_MAJOR = "%d" % int(eval("0x30"))

EV_ABS = "%d" % int(eval("0x3"))

EV_KEY = "%d" % int(eval("0x1"))
KEY_BACK = "%d" % int(eval("0x9e"))
KEY_HOMEPAGE = "%d" % int(eval("0xac"))

DOWN = "%d" % int(eval("0x1"))
UP = "%d" % int(eval("0x0"))

EV_SYN = "%d" % int(eval("0x0"))
SYN_REPORT = "%d" % int(eval("0x0"))
#======================================================
SENDEVENT_FROMADB = False
scale = 1
pressing = False
WIDTH = 0
HEIGHT = 0

def log(str, show=True):
    if (show):
        #top.title(str)
        print(str)

def getoriention():
    global WIDTH
    global HEIGHT
    if (WIDTH > HEIGHT):
        return "landscape"
    return "portrait"

def getgeometry():
    global WIDTH
    global HEIGHT
    global scale
    w = WIDTH
    h = HEIGHT
    ws = top.winfo_screenwidth()  
    hs = top.winfo_screenheight() - 100
    wscale = 1
    hscale = 1
    if (WIDTH > ws):
        wscale = ws / WIDTH
    if (HEIGHT > hs):
        hscale = hs / HEIGHT
    if (wscale > hscale):
        scale = hscale
    else:
        scale = wscale
    log("scale : " + str(scale))
    w = WIDTH * scale
    h = HEIGHT * scale
    # calculate position x, y  
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    geometry = '%dx%d+%d+%d' % (w, h, x, y + 10)
    return geometry

def recvfrom(list):
    global WIDTH
    global HEIGHT
    global udp_socket
    while True:
        log("waiting for data from phone ...")
        try :
            data= list.recv(1024)
        except:
            log("except")
            break
        data = data.decode()
        if (data == None or data == ""):
            break
        data = eval(data)
        log(data)
        if (data["cmd"] == "response_screensize"):
            WIDTH = data["w"]
            HEIGHT = data["h"]
            reset_frame()
        if (data["cmd"] == "response_udpserver"):
            udp_socket = UdpSocket(data["addr"], data["port"])
        import time
        time.sleep(1)

class TcpSocket:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("127.0.0.1", 8989))
        list = [self.s]
        log("启动线程")
        th = threading.Thread(target=recvfrom, args=(list))
        th.setDaemon(True)
        th.start()
    def senddata(self, data):
        self.s.sendall(data.encode("utf-8"))

class UdpSocket:
    def __init__(self, addr, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.s.connect(("10.0.1.114", 8990))
        self.s.connect((addr, port))

    def senddata(self, data):
        self.s.sendall(data.encode("utf-8"))

def scaled(value):
    global scale
    value = value / scale
    return int(value)

class ScreenTranform:
    def __init__(self):
        dict = {}
        dict["cmd"] = "request_screensize"
        if (tcp_socket != None):
            tcp_socket.senddata(str(dict) + "\r\n")
    
    def get_x(self, event):
        if (getoriention() == "landscape"):
            return str(HEIGHT - scaled(event.y))
        return str(scaled(event.x))

    def get_y(self, event):
        if (getoriention() == "landscape"):
            return str(scaled(event.x))
        return str(scaled(event.y))

class TouchEvent:
    EventJsonArray = None
    def addEvent(self, type, code, value):
        if (TouchEvent.EventJsonArray == None):
            TouchEvent.EventJsonArray = []
        data = {}
        data["type"] = type
        data["code"] = code
        data["value"] = value
        if (SENDEVENT_FROMADB):
            sendevent(data)
        TouchEvent.EventJsonArray += [data]
    def sendEvent(self):
        data = {}
        data["cmd"] = "touch"
        data["touch"] = TouchEvent.EventJsonArray

        global udp_socket
        if (udp_socket != None and SENDEVENT_FROMADB == False):
            udp_socket.senddata(str(data))
        TouchEvent.EventJsonArray = None

def sendevent(touch_event):
    cmdlist = ["adb", "shell", "sendevent", EV_TOUCH_DEVICE, touch_event["type"], touch_event["code"], touch_event["value"]]
    string = ""
    for item in range(0, len(cmdlist)):
        showstr = cmdlist[item]
        if (item > 3):
            showstr = hex(eval(cmdlist[item]))
            showstr = showstr[2:]
            if (item == 4 or item == 5):
                showstr = showstr.rjust(4, '0')
            else:
                showstr = showstr.rjust(8, '0')
        string += showstr + " "
    log(string)
    subprocess.call(cmdlist)

def mousenevent(event):
    #log("[Move] x : %d, y : %d" % (event.x, event.y))
    global udp_socket
    data = {}
    data["cmd"] = "request_position"
    data["x"] = scaled(event.x)
    data["y"] = scaled(event.y)
    if (udp_socket != None):
        udp_socket.senddata(str(data))

    if (pressing):
        touch_event = TouchEvent()
        touch_event.addEvent(EV_ABS, ABS_MT_POSITION_X, screenTransform.get_x(event))
        touch_event.addEvent(EV_ABS, ABS_MT_POSITION_Y, screenTransform.get_y(event))
        touch_event.addEvent(EV_ABS, ABS_MT_PRESSURE, "%d" % 0x35)
        touch_event.addEvent(EV_SYN, SYN_REPORT, "0")
        touch_event.sendEvent()
    

def mouse_left_down(event):
    global pressing
    global TRACKING_ID
    TRACKING_ID = TRACKING_ID + 1
    
    #huawei
    touch_event = TouchEvent()
    touch_event.addEvent("1", "%d" % int(eval("0x14a")), "%d" % 1)
    touch_event.addEvent(EV_ABS, "%d" % int(eval("0x2f")), "%d" % 0)
    touch_event.addEvent(EV_ABS, ABS_MT_SLOT, "0")
    touch_event.addEvent(EV_ABS, ABS_MT_TRACKING_ID, "%d" % TRACKING_ID)
    touch_event.addEvent(EV_ABS, ABS_MT_POSITION_X, screenTransform.get_x(event))
    touch_event.addEvent(EV_ABS, ABS_MT_POSITION_Y, screenTransform.get_y(event))
    touch_event.addEvent(EV_ABS, ABS_MT_PRESSURE, "%d" % 0x350)
    touch_event.addEvent(EV_ABS, ABS_MT_TOUCH_MAJOR, "%d" % 0x6)
    touch_event.addEvent(EV_SYN, SYN_REPORT, "0")
    touch_event.sendEvent()
    pressing = True

def mouse_left_up(event):
    global pressing
    #log("[Up] x : %d, y : %d, state : %d" % (event.x, event.y, event.state))
    pressing = False
    touch_event = TouchEvent()
    touch_event.addEvent(EV_ABS, ABS_MT_SLOT, "0")
    touch_event.addEvent(EV_ABS, ABS_MT_TRACKING_ID, "%d" % -1)
    touch_event.addEvent(EV_SYN, SYN_REPORT, "0")
    
    #Add for huawei
    touch_event.addEvent("1", "%d" % int(eval("0x14a")), "%d" % 0)
    touch_event.addEvent(EV_SYN, SYN_REPORT, "0")
    touch_event.sendEvent()


def process_click(key):
    touch_event = TouchEvent()
    touch_event.addEvent(EV_KEY, key, DOWN)
    touch_event.addEvent(EV_SYN, SYN_REPORT, "0")
    touch_event.addEvent(EV_KEY, key, UP)
    touch_event.addEvent(EV_SYN, SYN_REPORT, "0")
    touch_event.sendEvent()


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

def reset_frame():
    top.geometry(getgeometry())

def esc_click(event):
    top.quit()

def connect_phone():
    cmdlist = ["adb", "forward", "tcp:8989", "tcp:8989"]
    ret = subprocess.call(cmdlist)
    if (ret != 0):
        sys.exit(0)

def request_udp_server():
    data = {}
    data["cmd"] = "request_udpserver"
    if (tcp_socket != None):
        tcp_socket.senddata(str(data) + "\r\n")

top = tkinter.Tk()

connect_phone()
tcp_socket = TcpSocket()
udp_socket = None
#udp_socket = UdpSocket()
request_udp_server()
#th1 = threading.Thread(target=request_udp_server, args=())
#th1.setDaemon(True)
#th1.start()


screenTransform = ScreenTranform()


top.resizable(False,False)
top.geometry(getgeometry())
top.bind("<Motion>", mousenevent)
top.bind("<ButtonPress-1>", mouse_left_down)
top.bind("<ButtonRelease-1>", mouse_left_up)
top.bind("<Button-2>", mouse_middle_click)
top.bind("<Button-3>", mouse_right_click)
top.bind("<Key-F2>", f2_click)
#top.bind("<Key-F12>", f12_click)
top.bind("<Key-Escape>", esc_click)

top.mainloop()
log("quit")
