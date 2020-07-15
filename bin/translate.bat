@echo off
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (set pythonpath=%%i)
set  translate=script\translator\translator.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%translate%
echo [Logging...] 执行文件路径 : [%pythonpath%]
echo [Logging...] 翻译脚本路径 : [%translate%]
@rem echo curdir=%curdir%
@rem echo translate=%translate%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
