# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import Common
import Utils
import threading
'''
下载器
'''
class UrlManager:
    __instance = None
    __threadLock = threading.Lock()

    @staticmethod
    def getInstance():
        if(UrlManager.__instance == None):
            UrlManager.__threadLock.acquire()
            if(UrlManager.__instance == None):
                UrlManager.__instance = UrlManager()
            UrlManager.__threadLock.release()
        return UrlManager.__instance

    def __init__(self):
        self.__urlWithGrab = []
        self.__urlGrabbed = []

    def pushOne(self, url):
        logger.debug("pushOne : %s" % (url))
        UrlManager.__threadLock.acquire()
        if self.__exist(self.__urlGrabbed, url) == False:
            self.__pushUrlInternal(self.__urlWithGrab, url)
        UrlManager.__threadLock.release()

    def pushList(self, urllist):
        UrlManager.__threadLock.acquire()
        if urllist != None and len(urllist) > 0:
            for url in urllist:
                self.__pushUrlInternal(self.__urlWithGrab, url)
        UrlManager.__threadLock.release()

    def setGrabbedUrl(self, grabbedUrl):
        logger.debug("grabbedUrl : %s" % (grabbedUrl))
        UrlManager.__threadLock.acquire()
        self.__pushUrlInternal(self.__urlGrabbed, grabbedUrl)
        UrlManager.__threadLock.release()

    def pop(self):
        return self.__popFirst()

    def size(self):
        return len(self.__urlWithGrab)
    
    def hasUrl(self):
        return len(self.__urlWithGrab) > 0

    def grabbedList(self):
        return self.__urlGrabbed

    def __pushUrlInternal(self, urllist, url):
        exist = self.__exist(urllist, url)
        if exist == False:
            urllist.append(url)

    def __popFirst(self):
        return self.__urlWithGrab.pop(0)

    def __exist(self, l, item):
        try:
            return l.index(item) > -1
        except:
            return False