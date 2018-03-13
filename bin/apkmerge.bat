@echo off
set  pythonpath=C:\Python34\python.exe
set  apkmerge=script\apkmerger\mergeapk.py
set  curdir=%~dp0
set  fullpypath=%curdir%..\%apkmerge%
@rem echo curdir=%curdir%
@rem echo apkmerge=%apkmerge%
@rem echo pythonpath=%pythonpath%
@rem echo fullpypath=%fullpypath%
%pythonpath% %fullpypath% %1 %2 %3 %4 %5 %6 %7 %8 %9
