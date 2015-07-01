#!/usr/bin/python
# coding: UTF-8

import os
import sys
import shutil

def log(str, show=False):
    if (show):
        print(str)


def copy_res(gamefolder, payfolder):
    log("[Logging...] 正在拷贝资源文件", True)
    if (os.path.exists(gamefolder) == False):
        log("[Error...] 无法定位文件夹 %s" % gamefolder, True)
        sys.exit(0)
    if (os.path.exists(payfolder) == False):
        log("[Error...] 无法定位文件夹 %s" % payfolder, True)
        sys.exit(0)
    gameres = os.path.join(gamefolder, "res")
    payres = os.path.join(payfolder, "res")
    list = os.walk(payres, True)
    for root, dirs, files in list:
        for file in files:
            gamedir = root.replace(payfolder, gamefolder)
            payfile = os.path.join(root, file)
            if (os.path.exists(gamedir) == False):
                os.makedirs(gamedir)
            if (root.endswith("values") == False):

                gamefile = payfile.replace(payfolder, gamefolder)
                #log("payfile : %s , gamefile : %s " % (payfile, gamefile))
                shutil.copy2(payfile, gamefile)
            else:
                if (file != "public.xml"):
                    file = "ck_" + file
                    tmp = os.path.join(root, file)
                    gamefile = tmp.replace(payfolder, gamefolder)
                    #log("payfile : %s , gamefile : %s " % (payfile, gamefile))
                    shutil.copy2(payfile, gamefile)
    log("[Logging...] 拷贝资源文件完成\n", True)
    return True

if __name__ == "__main__":
    copy_res(sys.argv[1], sys.argv[2])