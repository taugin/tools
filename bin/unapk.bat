@echo off
set  curdir=%~dp0
set  filename=%~nx1
set  cmd7zfile=%curdir%7z.exe
set  filedir=%filename:~0,-4%
@rem echo curdir : %curdir%, filename : %filename% , 7zfile : %cmd7zfile%, cwd : %cd% , filedir : %filedir%
echo [Logging...] �ű��ļ�·�� : [%cmd7zfile%]
echo [Logging...] �ű�����·�� : [%filename%]
set command=%cmd7zfile% x -tzip -bd -y -o"%filedir%" "%filename%"
echo [Logging...] �ű��������� : [%command%]
SET TMPFOLDER=%TMP%
SET temp_extract_result_file=%TMPFOLDER%\temp_extract_result_file.txt
@rem echo [Logging...] ��ʱ�ļ����� : [%temp_extract_result_file%]
%command% > %temp_extract_result_file%
if 0 == %ERRORLEVEL% (
    del %temp_extract_result_file%
    ECHO [Logging...] �ļ���ѹ�ɹ�
    echo [Logging...] Wait for 3 seconds to exit
    ping localhost -n 5 > nul
) else (
    ECHO [Logging...] �ļ���ѹʧ��
    for /F "delims=" %%i in ('TYPE %temp_extract_result_file%') do (
        ECHO [Warning...] %%i
	)
    del %temp_extract_result_file%
    pause
)