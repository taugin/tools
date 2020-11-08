@echo off
:start
echo [Logging...] %date% %time%
rem 获取顶层应用
for /F "delims=" %%i in ('adb shell dumpsys activity top ^| findstr "ACTIVITY"') do (set ALL_ACTIVITY=%%i)
rem echo ALL_ACTIVITY=%ALL_ACTIVITY%

rem 获取包名
for /F "tokens=2 delims= " %%i in ("%ALL_ACTIVITY%") do (set TOP_ACTIVITY=%%i)
rem echo TOP_ACTIVITY=%TOP_ACTIVITY%

rem 获取包名
for /F "tokens=1 delims=/" %%i in ("%TOP_ACTIVITY%") do (set PACKAGE_NAME=%%i)
rem echo PACKAGE_NAME=%PACKAGE_NAME%

rem 获取类名
for /F "tokens=2 delims=/" %%i in ("%TOP_ACTIVITY%") do (set ACTIVITY_NAME=%%i)
rem echo ACTIVITY_NAME=%ACTIVITY_NAME%

echo [Logging...] PACKAGE_NAME : [%PACKAGE_NAME%] , ACTIVITY_NAME : [%ACTIVITY_NAME%]

echo.
choice /t 1 /d y /n >nul
goto start