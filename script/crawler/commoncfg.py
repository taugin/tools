#!/usr/bin/python
# coding: UTF-8

import sys
import os
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)

import logging
#import logging.handlers

#LOG_FILE = 'tst.log'

#handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)# 实例化handler
handler = logging.StreamHandler(); #输出到控制台
fmt = '[%(asctime)s - %(filename)s:%(lineno)s - %(name)s] : %(message)s'

formatter = logging.Formatter(fmt)# 实例化formatter
handler.setFormatter(formatter)# 为handler添加formatter

logger = logging.getLogger('crawler')# 获取名为tst的logger
logger.addHandler(handler)# 为logger添加handler
logger.setLevel(logging.DEBUG)