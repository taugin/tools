@echo off
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (set pythonpath=%%i)
set  createreg=script\base\createreg.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%createreg%
echo [Logging...] ִ���ļ�·�� : [%pythonpath%]
echo [Logging...] ����ű�·�� : [%createreg%]
@rem echo curdir=%curdir%
@rem echo createreg=%createreg%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
