@echo off
set  curdir=%~dp0
set  filepath=%~nx1
set  cmd7zfile=%curdir%7z.exe
set  filename=%filepath:~0,-4%
echo curdir : %curdir%, filepath : %filepath% , 7zfile : %cmd7zfile%, cwd : %cd% , filename : %filename%
echo [Logging...] �ű��ļ�·�� : [%cmd7zfile%]
echo [Logging...] �ű�����·�� : [%filepath%]
set command=%cmd7zfile% x -tzip -bd -y -o%filename% %filepath%
echo [Logging...] �ű��������� : [%command%]
%command% > nul
if 0 == %ERRORLEVEL% (ECHO [Logging...] �ļ���ѹ�ɹ�) else (ECHO [Logging...] �ļ���ѹʧ��)
echo [Logging...] Wait for 3 seconds to exit
ping localhost -n 5 > nul
