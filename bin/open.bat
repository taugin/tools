@echo off
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (set pythonpath=%%i)
set  opendir=script\base\open.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%opendir%
echo [Logging...] ִ���ļ�·�� : [%pythonpath%]
echo [Logging...] ����ű�·�� : [%opendir%]
@rem echo curdir=%curdir%
@rem echo opendir=%opendir%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
