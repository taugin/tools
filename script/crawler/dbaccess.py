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

dbinfo = {
          "host" : "106.14.185.49",
          "username" : "root",
          "password" : "taugin0426",
          "dbname" : "taugin",
          }
dbCursor = None
dbConnection = None
_threadLock = threading.Lock()

def _getConnection():
    global dbConnection
    if dbConnection == None:
        dbConnection = pymysql.connect(dbinfo["host"], dbinfo["username"], dbinfo["password"], dbinfo["dbname"], charset="utf8")
    return dbConnection

def _getCursor():
    global dbCursor
    if dbCursor == None:
        connection = _getConnection()
        if connection != None:
            dbCursor = connection.cursor(pymysql.cursors.DictCursor)
    return dbCursor

def execSql(sql):
    '''执行数据库语句'''
    _threadLock.acquire()
    logger.debug("=========>> execSql Start")
    result = -1
    try:
        _getCursor().execute(sql)
        result = _getCursor().lastrowid
        _getConnection().commit()
    except Exception as e:
        logger.debug("=========>> execSql e : %s" % e)
    logger.debug("=========>> execSql KeyId : %s" % result)
    _threadLock.release()
    return result

def fetchOne(sql):
    '''获取一条记录'''
    _threadLock.acquire()
    _getCursor().execute(sql)
    row = _getCursor().fetchone()
    _threadLock.release()
    return row

def fetchAll(sql):
    '''获取多条记录'''
    _threadLock.acquire()
    _getCursor().execute(sql)
    rows = _getCursor().fetchall()
    _threadLock.release()
    return rows

def rollback():
    _threadLock.acquire()
    _getConnection().rollback()
    _threadLock.release()

def closeConnection():
    _threadLock.acquire()
    if dbConnection != None:
        dbConnection.close()
    _threadLock.release()