@echo off
setlocal EnableDelayedExpansion

set FLAG=
if "%1" == "-d" (
    set FLAG=-d
    shift
) else if "%1" == "-e" (
    set FLAG=-e
    shift
)

if "%1" == "-c" (
    call :set_default_flag
    echo ********* Clean log cache ...
    adb !FLAG! wait-for-device
    adb !FLAG! logcat -c
    shift
)

call :set_tags %1 %2 %3 %4 %5 %6 %7 %8 %9

:logcat
echo ********* Wait for device connect ...
call :set_default_flag
adb !FLAG! wait-for-device
if "%1" == "" (
    adb !FLAG! shell setprop log.tag.hauyu V
    adb !FLAG! shell setprop log.tag.simple V
    adb !FLAG! shell setprop log.tag.mobsdk V
    echo ********* adb !FLAG! logcat -s simple hauyu mobsdk ...
    adb !FLAG! logcat -s simple hauyu mobsdk
) else (
    echo ********* adb !FLAG! logcat -s !TAGS!
    for %%a in (!TAGS!) do (
        adb !FLAG! shell setprop log.tag.%%a V
    )
    adb !FLAG! logcat -s !TAGS!
)

goto logcat

:set_default_flag
if not "!FLAG!" == "" goto :eof
set device_count=0
for /f "tokens=1,2" %%a in ('adb devices') do (
    if "%%b" == "device" (
        set /a device_count+=1
    )
)
if !device_count! GTR 1 (
    set FLAG=-d
)
goto :eof

:set_tags
if "%~1" == "" (
    set TAGS=simple hauyu mobsdk
) else (
    set TAGS=%*
)
goto :eof
