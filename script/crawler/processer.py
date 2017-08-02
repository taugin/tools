# coding: UTF-8
# 引入别的文件夹的模块

'''
setuptools下载地址
https://github.com/pypa/setuptools
mysql下载地址
https://github.com/PyMySQL/PyMySQL
执行  python setup.py install 安装
'''
from commoncfg import logger
import threading
import tempfile
import os
import dbaccess
import hashlib

md5 = hashlib.md5()
threadLock = threading.Lock()

def createProcesser():
    return JokeProcesser()

class Processer:
    def __init__(self):
        pass
    def __del__(self):
        pass
    def process(self, data):
        pass
class JokeProcesser(Processer):
    def process(self, data):
        threadLock.acquire()
        values = ""
        if data != None and 'title' in data and 'content' in data and 'pageurl' in data and 'pubtime' in data:
            md5.update(data['pageurl'].encode('utf-8'))
            urlmd5 = md5.hexdigest()
            values = " ('%s', '%s', '%s', '%s', FROM_UNIXTIME(%d))" % (data['title'], data['content'], data['pageurl'], urlmd5, data['pubtime'])
        else:
            threadLock.release()
            return
        sql = "insert into joke_ji(category, content, pageurl, urlmd5, pubtime) values"
        sql = sql + values;
        print(sql)
        try:
            dbaccess.execSql(sql)
        except Exception as e:
            dbaccess.rollback()
            logger.debug("error : %s" % str(e))
            '''
            rollback = os.path.join(tempfile.gettempdir(), 'rollback.txt')
            with open(rollback, "a", encoding="utf-8") as f:
                f.write("%s\n" % e)
            '''
        threadLock.release()
