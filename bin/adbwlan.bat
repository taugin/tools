@echo off
setlocal
echo [Logging...] Wait for usb device connected
adb wait-for-usb-device
echo [Logging...] Adb connected successfully
rem wlan的信息
for /F "delims=" %%i in ('adb shell netcfg ^| findstr "wlan"') do (set WLAN_INFO=%%i)
rem echo WLAN_INFO=%WLAN_INFO%

rem 获取手机ip地址信息
for /F "tokens=3 delims= " %%i in ("%WLAN_INFO%") do (set IP_ADDR_MASK=%%i)
rem echo IP_ADDR_MASK=%IP_ADDR_MASK%

rem 获取手机ip地址信息
for /F "tokens=1 delims=/" %%i in ("%IP_ADDR_MASK%") do (set IP_ADDR=%%i)
rem echo IP_ADDR=%IP_ADDR%
echo [Logging...] Current Phone IP Address : [%IP_ADDR%]
set ADB_PORT=9999
set adb_tcpip=adb tcpip %ADB_PORT%
echo [Logging...] TcpIp Command : [%adb_tcpip%]
%adb_tcpip%
set connect_cmd=adb connect %IP_ADDR%:%ADB_PORT%
echo [Logging...] Connect Command : [%connect_cmd%]
%connect_cmd%
pause