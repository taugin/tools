@echo off

set FILE1=%~dp0\jadx\bin\jadx-gui.bat
set FILE2=%~dp0\jadx_1.5.0_green\jadx-gui-1.5.0.exe

if exist "%FILE1%" goto run1
if exist "%FILE2%" goto run2
goto notFound

:run1
echo 正在执行 %FILE1%
call "%FILE1%" %*
goto end

:run2
echo 正在执行 %FILE2%
call "%FILE2%" %*
goto end

:notFound
echo 没有找到任何可执行的 .bat 文件

:end
