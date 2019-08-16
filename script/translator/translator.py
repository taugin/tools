'''
Created on 2019-8-16

@author: Administrator
'''
import translators_api
from translators_api.config import *
from collections import OrderedDict
import json

def calc_maxlen(all_language):
    max_len = 0
    for key in all_language.keys():
        if all_language[key] != None:
            ilen = len(all_language[key])
            if ilen > max_len:
                max_len = ilen
    return max_len

def show_all_support_language():
    max_len = calc_maxlen(LANGUAGES)
    all_languages = sorted(LANGUAGES.keys())
    index = 1
    for item in all_languages:
        c = LANGUAGES[item].split("|")[1]
        print("%3s : %s" % (index, c))
        index += 1

show_all_support_language()
