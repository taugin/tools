@echo off
rem 获取顶层应用
setlocal
rem 获取顶层应用
for /F "delims=" %%i in ('adb shell dumpsys activity top ^| findstr "ACTIVITY"') do (set ALL_ACTIVITY=%%i)
rem echo ALL_ACTIVITY=%ALL_ACTIVITY%

rem 获取包名
for /F "tokens=2 delims= " %%i in ("%ALL_ACTIVITY%") do (set TOP_ACTIVITY=%%i)
rem echo TOP_ACTIVITY=%TOP_ACTIVITY%

rem 获取包名
for /F "tokens=1 delims=/" %%i in ("%TOP_ACTIVITY%") do (set PACKAGE_NAME=%%i)
rem echo PACKAGE_NAME=%PACKAGE_NAME%

rem 获取进程数据
for /F "tokens=1 delims=" %%i in ('adb shell ps -A ^| findstr /c:"%PACKAGE_NAME%" /e') do (set PS_LINE=%%i)
rem echo PS_LINE=%PS_LINE%

rem 获取进程ID
for /F "tokens=2 delims= " %%i in ("%PS_LINE%") do (set PID=%%i)
rem echo PID=%PID%

echo [Logging...] %PID%      %PACKAGE_NAME%
set logcmd=adb logcat --pid=%PID%
echo [Logging...] Log Start : [%logcmd%]
%logcmd%