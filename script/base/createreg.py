import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR) 
sys.path.append(COM_DIR)

import Common
import getopt
import Log
from string import Template

THIS_FILE_DIR = os.path.dirname(sys.argv[0])
TEMP_TOOLS_ROOT = os.path.normpath(os.path.join(THIS_FILE_DIR, "..", ".."))
REG_TEMPLATE_FILE = os.path.join(TEMP_TOOLS_ROOT, "extra", "winreg", "reg.txt")
REG_TEMPLATE = None
with open(REG_TEMPLATE_FILE, "rb") as f:
    REG_TEMPLATE = f.read().decode()

TEMP_TOOLS_ROOT = TEMP_TOOLS_ROOT.replace("\\", "\\\\")
Log.out("[Logging...] 脚本执行参数 : [%s]" % TEMP_TOOLS_ROOT)

TEMP_WINRAR_PATH = "C:\Program Files\WinRAR\WinRar.exe"
TEMP_WINRAR_PATH = TEMP_WINRAR_PATH.replace("\\", "\\\\")
Log.out("[Logging...] 脚本执行参数 : [%s]" % TEMP_WINRAR_PATH)

TEMP_PYTHON_PATH = sys.executable
TEMP_PYTHON_PATH = TEMP_PYTHON_PATH.replace("\\", "\\\\")
Log.out("[Logging...] 脚本执行参数 : [%s]" % TEMP_PYTHON_PATH)

TEMP_CMD_PATH = os.popen("where cmd").readline().strip()
TEMP_CMD_PATH = TEMP_CMD_PATH.replace("\\", "\\\\")
Log.out("[Logging...] 脚本执行参数 : [%s]" % TEMP_CMD_PATH)

s = Template(REG_TEMPLATE)
output = s.substitute(WINRAR_PATH=TEMP_WINRAR_PATH,TOOLS_ROOT=TEMP_TOOLS_ROOT, PYTHON_PATH=TEMP_PYTHON_PATH, CMD_PATH=TEMP_CMD_PATH)
#Log.out("reg_template : %s" % output)

reg_file = os.path.join(TEMP_TOOLS_ROOT, "extra", "winreg", "out.reg")
f = open(reg_file, "w")
f.write(output)
f.close()
Log.out("[Logging...] 脚本执行参数 : [%s]" % reg_file)
Common.pause()