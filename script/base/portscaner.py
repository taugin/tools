#!/usr/bin/python
# coding: UTF-8
'''
端口扫面程序
'''
from threading import Thread, activeCount
import socket
import sys
import os
import re
import getopt
import signal
import time

SCANNING_STATUS = "正在扫描服务器 【%s】 端口 【%s】"
MIN_SCAN_PORT = 0; #最小端口
MAX_SCAN_PORT = 65536; #最大端口
SCANNING_IP = None
FORCE_EXIT = False

def log(out):
    print(out)

def pause(prompt):
    input(prompt)

def handler(signum, frame):
    global FORCE_EXIT
    FORCE_EXIT = True

def sleep(second):
    try:
        time.sleep(second)
    except:
        pass

def usage():
    basename = os.path.basename(sys.argv[0]);
    usagestr_title = "使用说明 "
    usagestr_uses = "%s [-h] -i <ip> -p <pstart-pend>\n" % basename
    usagestr_args = "\t-h 查看帮助\n\t-i 待扫描的IP地址\n\t-p 扫描的端口范围 : start-end\n"
    log(usagestr_title + usagestr_uses + usagestr_args)
    sys.exit()

def test_port(dst, port):
    sys.stdout.write(SCANNING_STATUS % (SCANNING_IP, str(port)) + '\r')
    sys.stdout.flush()
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        indicator = cli_sock.connect_ex((dst, port))
        if indicator == 0:
            sys.stdout.write(' ' * 100 + '\r')
            sys.stdout.write('已开启端口 : ')
            sys.stdout.flush()
            log(port)
        #log(socket.errorTab[indicator])
        cli_sock.close()
    except:
        pass

def port_scan():
    i = MIN_SCAN_PORT

    while i < MAX_SCAN_PORT and FORCE_EXIT == False:
        if activeCount() <= 200:
            Thread(target=test_port, args=(SCANNING_IP, i)).start()
            i = i + 1
            sleep(0.1)
    log('')
    log('')
    log("等待扫描线程退出")
    log('')
    while True:
        sys.stdout.write(' ' * 100 + '\r')
        sys.stdout.write("剩余活动线程数目 : [%d]\r" % activeCount())
        sys.stdout.flush()
        if activeCount() <= 2:
            break
        sleep(0.1)
    log("扫描结束")

def checkargs():
    if (SCANNING_IP == None):
        log("错误 : IP地址输入不合法")
        sys.exit()
    result = re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', SCANNING_IP)
    if (result == None):
        log("错误 : IP地址输入不合法")
        sys.exit()
    if (MIN_SCAN_PORT >= MAX_SCAN_PORT):
        log("错误 : 端口输入不合法")
        sys.exit()

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:p:")
        for op, value in opts:
            if (op == "-h"):
                usage()
            elif (op == "-i"):
                SCANNING_IP = value
            elif (op == "-p"):
                result = value.split("-")
                MIN_SCAN_PORT = int(result[0])
                MAX_SCAN_PORT = int(result[1])
    except:
        usage()

    checkargs()
    log("即将扫描服务器 [%s] 端口范围 [%d - %d]" % (SCANNING_IP, MIN_SCAN_PORT, MAX_SCAN_PORT))
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    port_scan()
