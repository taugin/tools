@echo off
setlocal
SET TMPFOLDER=%TMP%
SET connect_file=%TMPFOLDER%\adb_connect_tcpid.txt
SET cmd_connect_result_file=%TMPFOLDER%\cmd_connect_result.txt
echo [Logging...] Connect File : [%connect_file%]
IF EXIST %connect_file% (
	echo [Logging...] Read Connect Info From : [%connect_file%]
	for /F "delims=" %%i in ('TYPE %connect_file%') do (
		set cmd_connect=%%i
		goto :start1
	)
)
:start1
echo [Logging...] Exec Connect Info : [%cmd_connect%]
IF "%cmd_connect%" == "" goto :connect_usb_device
%cmd_connect% > %cmd_connect_result_file%

for /F "delims=" %%i in ('TYPE %cmd_connect_result_file%') do (
	set cmd_connect_result=%%i
	goto :start2
)
:start2
del %cmd_connect_result_file%

echo [Logging...] Exec Connect Result : [%cmd_connect_result%]

for /F "delims= " %%i in ("%cmd_connect_result%") do (
	set first_word=%%i
	goto :start3
)
:start3
rem echo first_word=%first_word%
IF "%first_word%" == "already" (
	goto :END
)
IF "%first_word%" == "connected" (
	goto :END
)

:connect_usb_device
set waitdevice=adb -d wait-for-usb-device
echo [Logging...] Wait for usb device connected : [%waitdevice%]
%waitdevice%
echo [Logging...] Adb connected successfully
rem wlan的信息
for /F "delims=" %%i in ('adb -d shell ip addr show wlan0 ^| findstr /c:"inet "') do (set WLAN_INFO=%%i)
rem echo WLAN_INFO=%WLAN_INFO%

rem 获取手机ip地址信息
for /F "tokens=2 delims= " %%i in ("%WLAN_INFO%") do (set IP_ADDR_MASK=%%i)
rem echo IP_ADDR_MASK=%IP_ADDR_MASK%

rem 获取手机ip地址信息
for /F "tokens=1 delims=/" %%i in ("%IP_ADDR_MASK%") do (set IP_ADDR=%%i)
rem echo IP_ADDR=%IP_ADDR%
echo [Logging...] Current Phone IP Address : [%IP_ADDR%]
set ADB_PORT=9999
set adb_tcpip=adb -d tcpip %ADB_PORT%
echo [Logging...] TcpIp Command : [%adb_tcpip%]
%adb_tcpip%
set connect_cmd=adb -d connect %IP_ADDR%:%ADB_PORT%
echo %connect_cmd% > %connect_file%
echo [Logging...] Connect Command : [%connect_cmd%]
%connect_cmd%
:END
echo [Logging...] Wait for 3 seconds to exit
ping localhost -n 5 > nul