@echo off
title APKתAAB
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (
		set pythonpath=%%i
		goto start
	)
:start
for /F "delims=" %%i in ('%pythonpath% --version') do (
		set pythonversion=%%i
	)
set  pythoncode=script\base\portscanner.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%pythoncode%
echo [Logging...] �ű��ļ�·�� : [%pythonpath%]
echo [Logging...] �ű��ļ��汾 : [%pythonversion%]
echo [Logging...] �ű�����·�� : [%pythoncode%]
echo.
@rem echo curdir=%curdir%
@rem echo pythoncode=%pythoncode%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9