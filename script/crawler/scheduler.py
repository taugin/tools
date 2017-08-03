# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import urlmanager
import threading
import downloader
import htmlparser
import time
import threadpool
import processer
import tempfile
import os
import dbaccess
import traceback
import sys

initUrl = "http://www.jokeji.cn/"
initUrl = "http://www.xiao688.com/"

RUNNING = True
threadNum = 1
pool = None
condition = threading.Condition()
urlManager = urlmanager.UrlManager()
downLoader = downloader.Downloader()
htmlParser = htmlparser.createParser()
htmlProcesser = processer.createProcesser()

def writeLastGrabUrl(url):
    tmpdir = tempfile.gettempdir()
    cfgfile = os.path.join(tmpdir, "crawler.cfg")
    with open(cfgfile, "w", encoding="utf-8") as file:
        file.write(url)

def readLastGrabUrl():
    tmpdir = tempfile.gettempdir()
    cfgfile = os.path.join(tmpdir, "crawler.cfg")
    if (os.path.exists(cfgfile) is False):
        return None
    with open(cfgfile, "r", encoding="utf-8") as file:
        url = file.read()
    os.remove(cfgfile)
    return url

def initGrabUrl():
    url = readLastGrabUrl()
    logger.debug("lastGrab : %s" % url)
    if url != None:
        urlManager.pushOne(url)
        htmlParser.setBaseUrl(url)
    else:
        htmlParser.setBaseUrl(initUrl)
        urlManager.pushOne(initUrl);

def hasForGrabbingUrl():
    '''查看是否有可抓取的URL'''
    return urlManager.hasUrl()

def fetchForGrabbingUrl():
    '''获取待抓取的URL'''
    return urlManager.pop()

def pushNewGrabUrl(urllist):
    '''防止新的待抓取的URL'''
    urlManager.pushList(urllist)

def fetchWebContent(url):
    '''抓取内容'''
    content = downLoader.download(url);
    return content

def parseContent(url, content):
    '''解析抓取的内容'''
    newurl, newdata = htmlParser.parse(url, content)
    if newurl == None:newurl = set()
    datalen = 0
    if newdata != None: datalen = len(newdata)
    logger.debug("url_size : %d, data_size : %d" % (len(newurl), datalen))
    return newurl, newdata

def processContent(data):
    htmlProcesser.process(data)

def writeToFile(name, content):
    f = open(name, mode="w", encoding="utf-8")
    f.write(content)
    f.close()

def grabbing(url):
    try:
        grabbingInternal(url)
    except:
        traceback.print_exc()

def grabbingInternal(url):
    logger.debug("Grabbing : %s" % url)
    if pool != None:
        logger.debug("Worksize : %d" % pool.workSize())
    '''实际抓取函数'''
    content = None
    try:
        content = fetchWebContent(url)
    except Exception as e:
        logger.debug("e : %s" % e)

    #writeToFile(time.strftime("yyyyMMdd") + ".html", content)
    newurl, newdata = parseContent(url, content)
    if (newurl != None and RUNNING):
        newList = list(newurl)
        urlManager.pushList(newList)
    processContent(newdata)
    writeLastGrabUrl(url)
    time.sleep(1)

def grabWorker(url):
    grabbing(url)
    if condition.acquire():
        condition.notify()
        condition.release()

class GrabThread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        grabbing(self.url)
        #工作线程结束，通知主线程
        #logger.debug(self.name + " over")
        if condition.acquire():
            condition.notify()
            condition.release()

def registerSignal():
    import signal
    signal.signal(signal.SIGINT, signal_handler) # 2
    signal.signal(signal.SIGTERM, signal_handler) # 15

def signal_handler(signum, frame):
    global RUNNING
    RUNNING = False
    logger.debug("signum : %d" % signum)

def grabWithMutilThread():
    while RUNNING:
        hasGrabUrl = hasForGrabbingUrl()
        if hasGrabUrl:
            activeCount = threading.activeCount()
            if activeCount < threadNum + 1:
                grabUrl = fetchForGrabbingUrl()
                logger.debug("开启抓取线程 leftsize : %d , grabsize : %d , url :%s" % (urlManager.size(), len(urlManager.grabbedList()), grabUrl))
                GrabThread(grabUrl).start()
            else:
                #logger.debug("等待有线程运行结束")
                if condition.acquire():
                    condition.wait();
                    condition.release()
        else:
            activeCount = threading.activeCount()
            logger.debug("未找到抓取URL 当前线程数 : %d" % activeCount)
            if activeCount > 1:
                try:
                    time.sleep(5);
                except:
                    pass
            else:
                logger.debug("抓取完毕，退出循环")
                break;

def grabWithThreadPool():
    global pool
    pool = threadpool.ThreadPool(threadNum)
    while RUNNING:
        hasGrabUrl = hasForGrabbingUrl()
        if hasGrabUrl:
            grabUrl = fetchForGrabbingUrl()
            if htmlProcesser.isGrabUrl(grabUrl):
                continue
            pool.addJob(grabWorker, grabUrl)
        else:
            size= pool.workSize()
            logger.debug("queueSize : %d, grabbedSize : %d" % (size, len(urlManager.grabbedList())))
            if (size > 0):
                if condition.acquire():
                    condition.wait()
                    condition.release()
            else:
                logger.debug("抓取完毕，退出循环")
                break;
    logger.debug("等待所有任务退出")
    pool.waitForComplete()

def cleanup():
    global htmlProcesser
    del htmlProcesser

def excepthook(t, value, trace):
    '''''write the unhandle exception to log'''
    print('Unhandled Error: %s: %s'%(str(t), str(value)))
    sys.__excepthook__(t, value, trace)

if __name__ == "__main__":
    registerSignal()
    sys.excepthook = excepthook
    initGrabUrl()
    grabWithThreadPool()
    #grabbing("http://www.jokeji.cn/yuanchuangxiaohua/jokehtml/xiaohuayoumo/2017080123561749.htm")
    #grabbing("http://www.xiao688.com/cms/article/id-139121.html")
    cleanup()
    logger.debug("Crawler over, grabbedSize : %s" % len(urlManager.grabbedList()));
