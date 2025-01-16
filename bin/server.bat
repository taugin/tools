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
echo [Logging...] 脚本文件路径 : [%pythonpath%]
echo [Logging...] 当前文件路径 : [%cd%]
echo.
@rem echo curdir=%curdir%
@rem echo pythoncode=%pythoncode%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% -m http.server -b 0.0.0.0
