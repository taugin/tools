@echo off
@rem set  pythonpath=C:\Users\liuzhao.wei\AppData\Local\Programs\Python\Python38-32\python.exe
for /F %%i in ('where python') do (set pythonpath=%%i)
set  excel2json=script\base\excel2json.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%excel2json%
echo [Logging...] ִ���ļ�·�� : [%pythonpath%]
echo [Logging...] ����ű�·�� : [%excel2json%]
@rem echo curdir=%curdir%
@rem echo excel2json=%excel2json%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
