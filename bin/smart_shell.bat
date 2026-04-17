@echo off

set TARGET=%~1
if "%TARGET%"=="" set TARGET=%CD%

where powershell >nul 2>nul
if %errorlevel%==0 (
    powershell.exe -NoExit -Command ^
    "$env:JAVA_TOOL_OPTIONS='-Dfile.encoding=UTF-8'; chcp 65001; Set-Location '%TARGET%';$Host.UI.RawUI.WindowTitle='Custom PowerShell Terminal'"
    exit
)

cmd.exe /k cd /d "%TARGET%" && chcp 65001 >nul