@echo off
set  curdir=%~dp0
set  filename=%~nx1
set  jar2dex=%curdir%\dex-tools-2.1\d2j-jar2dex.bat
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , jar2dex : %jar2dex%, cwd : %cd% , filedir : %filedir%
echo [Logging...] 脚本文件路径 : [%jar2dex%]
echo [Logging...] 脚本代码路径 : [%filename%]
set command=%jar2dex% %filename% --force
echo [Logging...] 脚本命令详情 : [%command%]
for /F "delims=" %%i in ('%command%') do (
	echo [Logging...] 命令执行详情 : %%i
)