@echo off
set  curdir=%~dp0
set jar_file=%curdir%..\lib\smali-2.4.0.jar
java -jar %jar_file%  %1 %2 %3 %4 %5 %6 %7 %8 %9
