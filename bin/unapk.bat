@echo off
set  curdir=%~dp0
set  filepath=%~nx1
set  cmd7zfile=%curdir%7z.exe
set  filename=%filepath:~0,-4%
echo curdir : %curdir%, filepath : %filepath% , 7zfile : %cmd7zfile%, cwd : %cd% , filename : %filename%
echo [Logging...] 脚本文件路径 : [%cmd7zfile%]
echo [Logging...] 脚本代码路径 : [%filepath%]
set command=%cmd7zfile% x -tzip -bd -y -o%filename% %filepath%
echo [Logging...] 脚本命令详情 : [%command%]
%command% > nul
if 0 == %ERRORLEVEL% (ECHO [Logging...] 文件解压成功) else (ECHO [Logging...] 文件解压失败)
echo [Logging...] Wait for 3 seconds to exit
ping localhost -n 5 > nul
