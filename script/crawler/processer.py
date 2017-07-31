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
'''
    def process(self, data):
        f = open("result.txt", "a", encoding="utf-8");
        if data != None and data['content'] != None:
            for d in data['content']:
                logger.debug("data : %s" % d)
                f.write(d)
                f.write("\n")
        f.close()
'''
threadLock = threading.Lock()
def createProcesser():
    return JokeProcesser()

class Processer:
    def __init__(self):
        self.db = pymysql.connect("localhost","root","123456","taugin", charset="utf8")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    def process(self, data):
        pass
class JokeProcesser(Processer):
    def process(self, data):
        threadLock.acquire()
        values = ""
        if data != None and data['content'] != None and len(data['content']) > 0:
            for d in data['content']:
                values += " ('%s', '%s', FROM_UNIXTIME(%d))," % (data['title'], d, data['pubtime'])
        else:
            threadLock.release()
            return
        sql = "insert into joke(category, content, pubtime) values"
        values = values[0:-1]
        sql = sql + values;
        print(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        threadLock.release()