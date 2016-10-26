#!/usr/bin/python
# coding: UTF-8
import sys
import os

path = None
if len(sys.argv) > 1:
    path = os.path.abspath(sys.argv[1])
else:
    path = os.getcwd()
#print(path)
os.startfile(path)