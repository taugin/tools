@echo off
chcp 65001 >nul
@rem set pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F "delims=" %%i in ('where python 2^>nul') do (
        set pythonpath=%%i
        goto start
    )
:start
if not defined pythonpath (
    echo [错误] 未找到 Python，请先安装 Python 3 并加入 PATH。
    exit /b 2
)
for /F "delims=" %%i in ('"%pythonpath%" --version') do (
        set pythonversion=%%i
    )

set pythoncode=script\android\check_aab_obfuscation.py
set curdir=%~dp0
set fullpypath=%curdir%..\%pythoncode%
echo [Logging...] 脚本文件路径 : [%pythonpath%]
echo [Logging...] 脚本文件版本 : [%pythonversion%]
echo [Logging...] 脚本代码路径 : [%pythoncode%]
echo.
@rem echo curdir=%curdir%
@rem echo pythoncode=%pythoncode%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
"%pythonpath%" "%fullpypath%" %*
