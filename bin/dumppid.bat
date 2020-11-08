@echo off
rem 获取顶层应用
for /F "delims=" %%i in ('adb shell dumpsys activity top ^| findstr "TASK"') do (set ALL_TASK=%%i)
rem echo ALL_TASK=%ALL_TASK%

rem 获取包名
for /F "tokens=2 delims= " %%i in ("%ALL_TASK%") do (set PACKAGE_NAME=%%i)
rem echo PACKAGE_NAME=%PACKAGE_NAME%


rem 获取进程数据
for /F "tokens=1 delims=" %%i in ('adb shell ps -A ^| findstr "%PACKAGE_NAME%"') do (set PS_LINE=%%i)
rem echo PS_LINE=%PS_LINE%

rem 获取用户ID
for /F "tokens=1 delims= " %%i in ("%PS_LINE%") do (set USER_ID=%%i)
rem echo USER_ID=%USER_ID%

echo [Logging...] %USER_ID%      %PACKAGE_NAME%
echo.

:start
echo [Logging...]  %date% %time%
adb shell ps -A | findstr "%USER_ID%"
echo.
choice /t 1 /d y /n >nul
goto start