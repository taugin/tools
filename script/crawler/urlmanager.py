# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import threading
'''
下载器
'''
class UrlManager:
    _instance = None
    _threadLock = threading.Lock()

    @staticmethod
    def getInstance():
        if(UrlManager._instance == None):
            UrlManager._threadLock.acquire()
            if(UrlManager._instance == None):
                UrlManager._instance = UrlManager()
            UrlManager._threadLock.release()
        return UrlManager._instance

    def __init__(self):
        self._urlWithGrab = []
        self._urlGrabbed = []

    def pushOne(self, url):
        logger.debug("pushOne : %s" % (url))
        UrlManager._threadLock.acquire()
        if self._exist(self._urlGrabbed, url) == False:
            self._pushUrlInternal(self._urlWithGrab, url)
        UrlManager._threadLock.release()

    def pushList(self, urllist):
        UrlManager._threadLock.acquire()
        if urllist != None and len(urllist) > 0:
            for url in urllist:
                if self._exist(self._urlGrabbed, url) == False:
                    self._pushUrlInternal(self._urlWithGrab, url)
        UrlManager._threadLock.release()

    def pop(self):
        UrlManager._threadLock.acquire()
        item = self._popFirst()
        self._pushUrlInternal(self._urlGrabbed, item)
        UrlManager._threadLock.release()
        return item

    def size(self):
        return len(self._urlWithGrab)
    
    def hasUrl(self):
        return len(self._urlWithGrab) > 0

    def grabbedList(self):
        return self._urlGrabbed

    def _pushUrlInternal(self, urllist, url):
        exist = self._exist(urllist, url)
        if exist == False:
            urllist.append(url)

    def _popFirst(self):
        return self._urlWithGrab.pop(0)

    def _exist(self, l, item):
        try:
            return l.index(item) > -1
        except:
            return False