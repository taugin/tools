@echo off
set  curdir=%~dp0
set  filename=%~nx1
set  dex2jar=%curdir%\dex-tools-2.1\d2j-dex2jar.bat
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , dex2jar : %dex2jar%, cwd : %cd% , filedir : %filedir%
echo [Logging...] �ű��ļ�·�� : [%dex2jar%]
echo [Logging...] �ű�����·�� : [%filename%]
set command=%dex2jar% %filename% --force
echo [Logging...] �ű��������� : [%command%]
for /F "delims=" %%i in ('%command%') do (
	echo [Logging...] ����ִ������ : %%i
)
pause