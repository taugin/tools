#!/usr/bin/python
# coding: UTF-8

import sys
import threading
import tkinter
import socket
import time
import subprocess

SENDEVENT_FROMADB = False
scale = 1
pressing = False
WIDTH = 0
HEIGHT = 0
AUTO_PRESS = False
AUTO_PRESS_X = 0
AUTO_PRESS_Y = 0
SENDEVENT_PROTOCOL = "tcp"

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
    def sendTcpData(self, data):
        self.s.sendall(data.encode("utf-8"))

class UdpSocket:
    def __init__(self, addr, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.s.connect(("10.0.1.114", 8990))
        self.s.connect((addr, port))

    def sendUdpData(self, data):
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
            tcp_socket.sendTcpData(str(dict) + "\r\n")
    
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
            sendEventFromUSB(data)
        TouchEvent.EventJsonArray += [data]
    def sendEvent(self):
        data = {}
        data["cmd"] = "touch"
        data["touch"] = TouchEvent.EventJsonArray

        global udp_socket
        if (udp_socket != None and SENDEVENT_FROMADB == False):
            udp_socket.sendUdpData(str(data))
        TouchEvent.EventJsonArray = None

def sendEventFromUSB(touch_event):
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
    global udp_socket
    send_touch_data(event, 2)

def mouse_left_down(event):
    global pressing
    pressing = True
    send_touch_data(event, 1)

def mouse_left_up(event):
    global AUTO_PRESS_X
    global AUTO_PRESS_Y
    global pressing
    pressing = False
    send_touch_data(event, 0)
    AUTO_PRESS_X = event.x
    AUTO_PRESS_Y = event.y

def send_touch_data(event, action):
    data = {}
    data["source"] = 1
    data["type"] = 0
    data["slot"] = 0
    data["action"] = action
    data["pressed"] = 0
    if (pressing):
        data["pressed"] = 1
    data["x"] = scaled(event.x)
    data["y"] = scaled(event.y)
    sendTouchOrKeyData(data)

def process_click(key):
    data = {}
    data["source"] = 1
    data["type"] = 1
    data["key"] = key
    data["state"] = 2
    sendTouchOrKeyData(data)

def sendTouchOrKeyData(data):
    if (SENDEVENT_PROTOCOL == "udp"):
        if (udp_socket != None):
            udp_socket.sendUdpData(str(data))
    elif (SENDEVENT_PROTOCOL == "tcp"):
        tcpdata = {}
        tcpdata["cmd"] = "touch"
        tcpdata["touch"] = str(data)
        if (tcp_socket != None):
            tcp_socket.sendTcpData(str(tcpdata) + "\r\n")

def mouse_right_click(event):
    process_click(0)

def mouse_middle_click(event):
    process_click(1)

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
        tcp_socket.sendTcpData(str(data) + "\r\n")

def click_automaticly():
    global AUTO_PRESS
    global AUTO_PRESS_X
    global AUTO_PRESS_Y
    event = tkinter.Event()
    while AUTO_PRESS:
        event.x = AUTO_PRESS_X
        event.y = AUTO_PRESS_Y
        mouse_left_up(event)
        mouse_left_down(event)

def start_thread(event):
    global AUTO_PRESS
    AUTO_PRESS = True
    th1 = threading.Thread(target=click_automaticly, args=())
    th1.setDaemon(True)
    th1.start()

def stop_thread(event):
    global AUTO_PRESS
    AUTO_PRESS = False

top = tkinter.Tk()

connect_phone()
tcp_socket = TcpSocket()
udp_socket = None
#udp_socket = UdpSocket()
request_udp_server()



screenTransform = ScreenTranform()


top.resizable(False,False)
top.geometry(getgeometry())
top.bind("<Motion>", mousenevent)
top.bind("<ButtonPress-1>", mouse_left_down)
top.bind("<ButtonRelease-1>", mouse_left_up)
top.bind("<Button-2>", mouse_middle_click)
top.bind("<Button-3>", mouse_right_click)
top.bind("<Key-F2>", f2_click)
top.bind("<Key-F3>", lambda event:start_thread(event))
top.bind("<Key-F4>", lambda event:stop_thread(event))
#top.bind("<Key-F12>", f12_click)
top.bind("<Key-Escape>", esc_click)

top.mainloop()
log("quit")
