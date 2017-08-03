#!/usr/bin/python
# coding: UTF-8

import os
import logging.handlers
import tempfile

LOG_FILE = os.path.join(tempfile.gettempdir(), 'tst.log')

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)# 实例化handler
handler_c = logging.StreamHandler(); #输出到控制台
fmt = '[%(asctime)s - %(filename)+13s:%(lineno)+3s - %(name)s] : %(message)s'

formatter = logging.Formatter(fmt)# 实例化formatter
handler.setFormatter(formatter)# 为handler添加formatter
handler_c.setFormatter(formatter)# 为handler添加formatter

logger = logging.getLogger('crawler')# 获取名为tst的logger
logger.addHandler(handler)# 为logger添加handler
logger.addHandler(handler_c)# 为logger添加handler
logger.setLevel(logging.DEBUG)