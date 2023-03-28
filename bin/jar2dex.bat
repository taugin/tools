@echo off
set  curdir=%~dp0
set  filename=%~nx1
@rem set  jar2dex=%curdir%\dex-tools-2.1\d2j-jar2dex.bat
set  jar2dex=%curdir%\..\lib\d8.jar
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , jar2dex : %jar2dex%, cwd : %cd% , filedir : %filedir%
echo [Logging...] 脚本文件路径 : [%jar2dex%]
echo [Logging...] 脚本代码路径 : [%filename%]
@rem set command_old=%jar2dex% %filename% --force
set command=java -jar %jar2dex% --output . %filename%
echo [Logging...] 脚本命令详情 : [%command%]
for /F "delims=" %%i in ('%command%') do (
	echo [Logging...] 命令执行详情 : %%i
)
pause