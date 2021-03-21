@echo off
set  curdir=%~dp0
set  filename=%~nx1
set  cmd7zfile=%curdir%7z.exe
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , 7zfile : %cmd7zfile%, cwd : %cd% , filedir : %filedir%
echo [Logging...] 脚本文件路径 : [%cmd7zfile%]
echo [Logging...] 脚本代码路径 : [%filename%]
set command=%cmd7zfile% x -tzip -bd -y -o"%filedir%" "%filename%"
echo [Logging...] 脚本命令详情 : [%command%]
SET TMPFOLDER=%TMP%
SET temp_extract_result_file=%TMPFOLDER%\temp_extract_result_file.txt
@rem echo [Logging...] 临时文件名称 : [%temp_extract_result_file%]
%command% > %temp_extract_result_file%
if 0 == %ERRORLEVEL% (
    del %temp_extract_result_file%
    ECHO [Logging...] 文件解压成功
    echo [Logging...] Wait for 3 seconds to exit
    ping localhost -n 5 > nul
) else (
    ECHO [Logging...] 文件解压失败
    for /F "delims=" %%i in ('TYPE %temp_extract_result_file%') do (
        ECHO [Warning...] %%i
	)
    del %temp_extract_result_file%
    pause
)