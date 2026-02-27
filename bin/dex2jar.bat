@echo off
set  curdir=%~dp0
set  filename=%~nx1
set  dex2jar=%curdir%\dex-tools-v2.4\d2j-dex2jar.bat
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , dex2jar : %dex2jar%, cwd : %cd% , filedir : %filedir%
echo [Logging...] 脚本文件路径 : [%dex2jar%]
echo [Logging...] 脚本代码路径 : [%filename%]
set command=%dex2jar% %filename% --force
echo [Logging...] 脚本命令详情 : [%command%]
for /F "delims=" %%i in ('%command%') do (
	echo [Logging...] 命令执行详情 : %%i
)
pause