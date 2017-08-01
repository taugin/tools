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
import pymysql
import threading
import tempfile
import os

threadLock = threading.Lock()

def createProcesser():
    return JokeProcesser()

class Processer:
    def __init__(self):
        self.db = pymysql.connect("106.14.185.49","root","taugin0426","taugin", charset="utf8")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    def process(self, data):
        pass
class JokeProcesser(Processer):
    def process(self, data):
        threadLock.acquire()
        values = ""
        if data != None and 'title' in data and 'content' in data and 'pageurl' in data and 'pubtime' in data:
            values = " ('%s', '%s', '%s', FROM_UNIXTIME(%d))" % (data['title'], data['content'], data['pageurl'], data['pubtime'])
        else:
            threadLock.release()
            return
        sql = "insert into joke_ji(category, content, pageurl, pubtime) values"
        sql = sql + values;
        print(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            rollback = os.path.join(tempfile.gettempdir(), 'rollback.txt')
            with open(rollback, "a", encoding="utf-8") as f:
                f.write("%s\n" % e)
        threadLock.release()
