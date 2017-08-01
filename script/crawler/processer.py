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
threadLock = threading.Lock()
def createProcesser():
    return JokeProcesser()

class Processer:
    def __init__(self):
        self.db = pymysql.connect("localhost","root","taugin0426","taugin", charset="utf8")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    def process(self, data):
        pass
class JokeProcesser(Processer):
    def process(self, data):
        logger.debug("start process...")
        threadLock.acquire()
        values = ""
        if data != None and "content" in data and len(data['content']) > 0:
            for d in data['content']:
                values += " ('%s', '%s', '%s', FROM_UNIXTIME(%d))," % (data['title'], d, data['pageurl'], data['pubtime'])
        else:
            threadLock.release()
            logger.debug("end process null data...")
            return
        sql = "insert into joke_ji(category, content, pageurl, pubtime) values"
        values = values[0:-1]
        sql = sql + values;
        print(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.debug("rollback e : %s" % e)
        threadLock.release()
        logger.debug("end process...")