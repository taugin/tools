@echo off
setlocal
adb disconnect
echo [Logging...] Wait for 3 seconds to exit
ping localhost -n 5 > nul