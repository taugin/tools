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
        if data != None and 'title' in data and 'content' in data and 'pageurl' in data and 'pubtime' in data:
            values = " ('%s', '%s', '%s', FROM_UNIXTIME(%d))" % (data['title'], data['content'], data['pageurl'], data['pubtime'])
        else:
            threadLock.release()
            logger.debug("end process null data...")
            return
        sql = "insert into joke_xiao688(category, content, pageurl, pubtime) values"
        sql = sql + values;
        print(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.debug("rollback e : %s" % e)
            with open("tmp.file", "a") as f:
                f.write("rollback e : %s\n" % e)
        threadLock.release()
        logger.debug("end process...")