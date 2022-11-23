@echo off
set  curdir=%~dp0
set jar_file=%curdir%..\lib\diffuse-0.1.0-binary.jar
java -jar %jar_file%  %1 %2 %3 %4 %5 %6 %7 %8 %9
