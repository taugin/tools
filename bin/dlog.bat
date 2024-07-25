@echo off
set argc=0
for %%x in (%*) do (
    set /a argc+=1
)
@rem echo %argc%
:logcat
echo ********* Wait for device connect ...
adb wait-for-device
if "%1" == "-c" (
    echo ********* Clean log cache ...
    adb logcat -c
    exit
)
if %argc% == 0 (
    adb shell setprop log.tag.hauyu V
    adb shell setprop log.tag.simple V
    adb shell setprop log.tag.mobsdk V
    echo ********* adb logcat -s simple hauyu mobsdk ...
    adb logcat -s simple hauyu mobsdk
) else (
    echo ********* adb logcat -s %1 %2 %3 %4 %5 %6 %7 %8 %9
    for %%a in (%*) do (
        adb shell setprop log.tag.%%a V
    )
    adb logcat -s %1 %2 %3 %4 %5 %6 %7 %8 %9
)

goto logcat