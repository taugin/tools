@echo off
set argc=0
for %%x in (%*) do (
    set /a argc+=1
)
@rem echo %argc%
echo ********* Wait for device connect ...
adb wait-for-device
set package_name=%1
set install_referrer="https://play.google.com/store/apps/details?id=%package_name%&referrer=utm_source%%3Dgoogle%%26utm_medium%%3Dcpc%%26utm_term%%3Dshoes%%26utm_content%%3Dlogolink%%26utm_campaign%%3Dspring_sale%%26gclid%%3Dadegadetwd3aer"
if %argc% GTR 0 (
    adb shell am start -a android.intent.action.VIEW -d "https://play.google.com/store/apps/details?id=%package_name%&referrer=utm_source%3Dgoogle%26utm_medium%3Dcpc%26gclid%3Dadegadetwd3aer"
) else (
    echo MISS PACKAGE NAME
)
