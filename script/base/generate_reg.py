REG_TEMPLATE = \
'''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\myapkfile]
@=""
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\myapkfile\DefaultIcon]
@="$TOOLS_ROOT\\\\extra\\\\winreg\\\\android.ico,0"

[HKEY_CLASSES_ROOT\myapkfile\shell]

[HKEY_CLASSES_ROOT\myapkfile\shell\open]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\android.ico,0"

[HKEY_CLASSES_ROOT\myapkfile\shell\open\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\sf.py -i \\"%1\\""

[HKEY_CLASSES_ROOT\myapkfile\shell\为APK签名]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\qian.ico,0"

[HKEY_CLASSES_ROOT\myapkfile\shell\为APK签名\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\signapk.py \\"%1\\""

[HKEY_CLASSES_ROOT\myapkfile\shell\使用WinRAR打开]
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\myapkfile\shell\使用WinRAR打开\command]
@="$WINRAR_PATH \\"%1\\""

[HKEY_CLASSES_ROOT\myapkfile\shell\查看APK信息]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\cha.ico,0"

[HKEY_CLASSES_ROOT\myapkfile\shell\查看APK信息\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\sf.py -p \\"%1\\""

#[HKEY_CLASSES_ROOT\myapkfile\shell\为APK加壳]

#[HKEY_CLASSES_ROOT\myapkfile\shell\为APK加壳\command]
#@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\modapk.py -e \\"%1\\""

#[HKEY_CLASSES_ROOT\myapkfile\shell\生成调试APK]

#[HKEY_CLASSES_ROOT\myapkfile\shell\生成调试APK\command]
#@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\modapk.py -j \\"%1\\""

[HKEY_CLASSES_ROOT\myapkfile\shell\反编译]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\fan.ico,0"

[HKEY_CLASSES_ROOT\myapkfile\shell\反编译\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\apktool.py d \\"%1\\" -f"

[HKEY_CLASSES_ROOT\myapkfile\shell\APK对齐\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\signapk.py -a \\"%1\\""

[HKEY_CLASSES_ROOT\mydexfile\shell\DEX2JAR]
"Icon"="$CMD_PATH"

[HKEY_CLASSES_ROOT\mydexfile\shell\DEX2JAR\command]
@="$TOOLS_ROOT\\\\bin\\\\dex2jar-2.0\\\\d2j-dex2jar.bat \\"%1\\""

[HKEY_CLASSES_ROOT\myapkfile\shell\JADX-GUI]
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\myapkfile\shell\JADX-GUI\command]
@="$TOOLS_ROOT\\\\bin\\\\jadx\\\\bin\\\\jadx-gui.bat \\"%1\\""

[HKEY_CLASSES_ROOT\.apk]
@="myapkfile"

[HKEY_CLASSES_ROOT\myaarfile]
@=""
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\myaarfile\DefaultIcon]
@="$TOOLS_ROOT\\\\extra\\\\winreg\\\\android.ico,0"

[HKEY_CLASSES_ROOT\myaarfile\shell]

[HKEY_CLASSES_ROOT\myaarfile\shell\使用WinRAR打开]
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\myaarfile\shell\使用WinRAR打开\command]
@="$WINRAR_PATH \\"%1\\""

[HKEY_CLASSES_ROOT\.aar]
@="myaarfile"

[HKEY_CLASSES_ROOT\myjarfile\shell\open]
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\myjarfile\shell\open\command]
@="$WINRAR_PATH \\"%1\\""

[HKEY_CLASSES_ROOT\myjarfile\shell\JD-GUI]
"Icon"="$TOOLS_ROOT\\\\bin\\\\jd-gui.exe"

[HKEY_CLASSES_ROOT\myjarfile\shell\JD-GUI\command]
@="$TOOLS_ROOT\\\\bin\\\\jd-gui.exe \\"%1\\""

[HKEY_CLASSES_ROOT\.jar]
@="myjarfile"

[HKEY_CLASSES_ROOT\Directory\shell\命令提示符]
"Icon"="$CMD_PATH"

[HKEY_CLASSES_ROOT\Directory\shell\命令提示符\command]
@="cmd /k cd %1"

[HKEY_CLASSES_ROOT\Directory\shell\编译APK]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\hui.ico,0"

[HKEY_CLASSES_ROOT\Directory\shell\编译APK\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\apktool.py b \\"%1\\" -o \\"%1-recompile.apk\\""

[HKEY_CLASSES_ROOT\*\shell\查看MD5和SHA1]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\md5.ico,0"

[HKEY_CLASSES_ROOT\*\shell\查看MD5和SHA1\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\sf.py -m \\"%1\\""

[HKEY_CLASSES_ROOT\*\shell\AES加密]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\jia.ico,0"

[HKEY_CLASSES_ROOT\*\shell\AES加密\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\aes.py -e -k 123456789 -i \\"%1\\""

[HKEY_CLASSES_ROOT\*\shell\AES解密]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\jie.ico,0"

[HKEY_CLASSES_ROOT\*\shell\AES解密\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\aes.py -d -k 123456789 -i \\"%1\\""

[HKEY_CLASSES_ROOT\Directory\Background\shell\PullApk]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\android.ico,0"

[HKEY_CLASSES_ROOT\Directory\Background\shell\PullApk\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\pullapk.py"

#
[HKEY_CLASSES_ROOT\mydexfile\shell\open]
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\mydexfile\shell\open\command]
@="$TOOLS_ROOT\\\\bin\\\\jadx\\\\bin\\\\jadx-gui.bat \\"%1\\""

[HKEY_CLASSES_ROOT\mydexfile\shell\JADX-GUI]
"Icon"="$WINRAR_PATH"

[HKEY_CLASSES_ROOT\mydexfile\shell\JADX-GUI\command]
@="$TOOLS_ROOT\\\\bin\\\\jadx\\\\bin\\\\jadx-gui.bat \\"%1\\""

[HKEY_CLASSES_ROOT\mydexfile\shell\DEX2JAR]
"Icon"="$CMD_PATH"

[HKEY_CLASSES_ROOT\mydexfile\shell\DEX2JAR\command]
@="$TOOLS_ROOT\\\\bin\\\\dex2jar-2.0\\\\d2j-dex2jar.bat \\"%1\\""

[HKEY_CLASSES_ROOT\.dex]
@="mydexfile"

[HKEY_CLASSES_ROOT\*\shell\Excel2Json]
"Icon"="$TOOLS_ROOT\\\\extra\\\\winreg\\\\zhuan.ico,0"

[HKEY_CLASSES_ROOT\*\shell\Excel2Json\command]
@="$PYTHON_PATH $TOOLS_ROOT\\\\script\\\\base\\\\adsdk.py \\"%1\\""
'''

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
TEMP_TOOLS_ROOT = TEMP_TOOLS_ROOT.replace("\\", "\\\\")
Log.out("TEMP_TOOLS_ROOT : \t%s" % TEMP_TOOLS_ROOT)

TEMP_WINRAR_PATH = "C:\Program Files\WinRAR\WinRar.exe"
TEMP_WINRAR_PATH = TEMP_WINRAR_PATH.replace("\\", "\\\\")
Log.out("TEMP_WINRAR_PATH : \t%s" % TEMP_WINRAR_PATH)

TEMP_PYTHON_PATH = sys.executable
TEMP_PYTHON_PATH = TEMP_PYTHON_PATH.replace("\\", "\\\\")
Log.out("TEMP_PYTHON_PATH : \t%s" % TEMP_PYTHON_PATH)

TEMP_CMD_PATH = os.popen("where cmd").readline().strip()
TEMP_CMD_PATH = TEMP_CMD_PATH.replace("\\", "\\\\")
Log.out("TEMP_CMD_PATH : \t%s" % TEMP_CMD_PATH)

s = Template(REG_TEMPLATE)
output = s.substitute(WINRAR_PATH=TEMP_WINRAR_PATH,TOOLS_ROOT=TEMP_TOOLS_ROOT, PYTHON_PATH=TEMP_PYTHON_PATH, CMD_PATH=TEMP_CMD_PATH)
#Log.out("reg_template : %s" % output)

reg_file = os.path.join(TEMP_TOOLS_ROOT, "extra", "winreg", "out.reg")
f = open(reg_file, "w")
f.write(output)
f.close()