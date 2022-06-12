@echo off
set  curdir=%~dp0
set bundle_tool_jar=%curdir%..\lib\bundletool-all-1.6.1.jar
java -jar %bundle_tool_jar%  %1 %2 %3 %4 %5 %6 %7 %8 %9
