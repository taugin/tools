@echo off
setlocal
adb disconnect
echo [Logging...] Wait for 2 seconds to exit
ping localhost -n 3 > nul