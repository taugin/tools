@echo off
set  curdir=%~dp0
set  filename=%~nx1
set  jar2dex=%curdir%\dex-tools-2.1\d2j-jar2dex.bat
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , jar2dex : %jar2dex%, cwd : %cd% , filedir : %filedir%
echo [Logging...] �ű��ļ�·�� : [%jar2dex%]
echo [Logging...] �ű�����·�� : [%filename%]
set command=%jar2dex% %filename% --force
echo [Logging...] �ű��������� : [%command%]
for /F "delims=" %%i in ('%command%') do (
	echo [Logging...] ����ִ������ : %%i
)