@echo off
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (set pythonpath=%%i)
set  apkmerge=script\apkmerger\mergeapk.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%apkmerge%
echo [Logging...] 执行文件路径 : [%pythonpath%]
@rem echo curdir=%curdir%
@rem echo apkmerge=%apkmerge%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
