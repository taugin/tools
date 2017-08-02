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
import hashlib

dbinfo = {
          "host" : "106.14.185.49",
          "username" : "root",
          "password" : "taugin0426",
          "dbname" : "taugin",
          "tname" : "joke_ji"
          }
dbCursor = None
dbConnection = None
def getConnection():
    global dbConnection
    if dbConnection == None:
        dbConnection = pymysql.connect(dbinfo["host"], dbinfo["username"], dbinfo["password"], dbinfo["dbname"], charset="utf8")
    return dbConnection

def getCursor():
    global dbCursor
    if dbCursor == None:
        connection = getConnection()
        if connection != None:
            dbCursor = connection.cursor(pymysql.cursors.DictCursor)
    return dbCursor

def execSql(sql):
    getCursor().execute(sql)
    getConnection().commit()

def fetchOne(sql):
    getCursor().execute(sql)
    row = getCursor().fetchone()
    return row

def fetchAll(sql):
    getCursor().execute(sql)
    rows = getCursor().fetchall()
    return rows

def rollback():
    getConnection().rollback()

def closeConnection():
    if dbConnection != None:
        dbConnection.close()