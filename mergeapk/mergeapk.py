#!/usr/bin/python
# coding: UTF-8

import sys
import decompile_apk
import compile_apk

compile_apk.apk_compile(sys.argv[1], sys.argv[2])