@echo off
echo ==========================
echo   Proxy ON
echo ==========================

set http_proxy=http://127.0.0.1:10808
set https_proxy=http://127.0.0.1:10808
set all_proxy=socks5://127.0.0.1:10808

echo http_proxy=%http_proxy%
echo https_proxy=%https_proxy%
echo all_proxy=%all_proxy%

echo.
echo Proxy enabled for this CMD session.
pause