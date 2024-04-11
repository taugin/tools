@echo off
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (
		set pythonpath=%%i
		goto start
	)
:start
for /F "delims=" %%i in ('%pythonpath% --version') do (
		set pythonversion=%%i
	)
set  pythoncode=script\elf\lief_modify_function.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%pythoncode%
echo [Logging...] 脚本文件路径 : [%pythonpath%]
echo [Logging...] 脚本文件版本 : [%pythonversion%]
echo [Logging...] 脚本代码路径 : [%pythoncode%]
echo.
@rem echo curdir=%curdir%
@rem echo pythoncode=%pythoncode%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
