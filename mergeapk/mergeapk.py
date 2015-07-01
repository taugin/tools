#!/usr/bin/python
# coding: UTF-8

import os
import sys
import decompile_apk
import compile_apk
import check_dup
import rebuild_ids
import copy_res
import merge_xml
import copy_fromapk

def log(str, show=True):
    if (show):
        print(str)

gameapk = os.path.abspath(sys.argv[1])
payapk = os.path.abspath(sys.argv[2])

(name, ext) = os.path.splitext(gameapk)
gamefolder = name
gamemergedapk = name + "-merged.apk"
(name, ext) = os.path.splitext(payapk)
payfolder = name

decompile_apk.apk_decompile(gameapk, gamefolder)
decompile_apk.apk_decompile(payapk, payfolder)

check_dup.check_dup(gamefolder, payfolder)
rebuild_ids.rebuild_ids(gamefolder, payfolder)
copy_res.copy_res(gamefolder, payfolder)
merge_xml.merge_xml(gamefolder, payfolder)

compile_apk.apk_compile(gamefolder, gamemergedapk)
copy_fromapk.copy_fromapk(gamemergedapk, gameapk, payapk)