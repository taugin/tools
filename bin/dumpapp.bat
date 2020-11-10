@echo off

:start
echo [Logging...] ARGS : [%*]
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

rem 获取进程数据
for /F "tokens=1 delims=" %%i in ('adb shell ps -A ^| findstr "%PACKAGE_NAME%"') do (set PS_LINE=%%i)
rem echo PS_LINE=%PS_LINE%

rem 获取用户ID
for /F "tokens=1 delims= " %%i in ("%PS_LINE%") do (set USER_ID=%%i)
rem echo USER_ID=%USER_ID%

echo [Logging...] USER_ID : [%USER_ID%] , PACKAGE_NAME : [%PACKAGE_NAME%] , ACTIVITY_NAME : [%ACTIVITY_NAME%]

adb shell ps -A | findstr "%USER_ID%"
rem if not "%ERRORLEVEL%" == "0" (
rem echo [Logging...]  Can not get content, exit...
rem goto end
rem )


echo.
rem choice /t 1 /d y /n >nul
ping localhost -n 2 > nul
if "%1" == "loop" (goto start)