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
import dbaccess
import hashlib

md5 = hashlib.md5()
_threadLock = threading.Lock()

def createProcesser():
    return JokeProcesser()

class Processer:
    def __init__(self):
        pass

    def __del__(self):
        dbaccess.closeConnection()

    def process(self, data):
        pass

class JokeProcesser(Processer):
    def __init__(self):
        self.table = {}
        self.table['grab'] = "joke_ji"
        self.table['error_grab'] = "error_url_grab"

    def process(self, data):
        if data == None:
            return
        if "content" in data and data["content"] != None and len(data["content"]) > 0:
            self.addGrabContent(data)
        '''不在存储错误url
        else:
            self.addErrorInfo(data)
        '''

    def hasGrabbed(self, url):
        '''判断当前url是否被抓取过'''
        md5=hashlib.md5(url.encode('utf-8')).hexdigest()
        sql = "select id from %s where urlmd5='%s'" % (self.table['grab'], md5)
        return dbaccess.fetchOne(sql) != None

    def addGrabContent(self, data):
        values = " ('%s', '%s', '%s', '%s', FROM_UNIXTIME(%d))" % (data['title'], data['content'], data['pageurl'], data['urlmd5'], data['pubtime'])
        sql = "insert into %s(title, content, pageurl, urlmd5, pubtime) values" % self.table['grab']
        sql = sql + values
        try:
            dbaccess.execSql(sql)
        except Exception as e:
            dbaccess.rollback()
            logger.debug("error : %s" % str(e))

    def addErrorInfo(self, data):
        values = " ('%s', '%s', FROM_UNIXTIME(%d))" % (data['pageurl'], data['urlmd5'], data['pubtime'])
        sql = "insert into %s(pageurl, urlmd5, pubtime) values" % self.table['error_grab']
        sql = sql + values
        try:
            dbaccess.execSql(sql)
        except Exception as e:
            dbaccess.rollback()
            logger.debug("error : %s" % str(e))