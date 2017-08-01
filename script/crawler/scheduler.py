# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import Common
import Utils
import urlmanager
import threading
import downloader
import htmlparser
import time
import threadpool
import processer
from distutils.command.config import config

RUNNING = True
threadNum = 10
condition = threading.Condition()
urlManager = urlmanager.UrlManager()
downLoader = downloader.Downloader()
htmlParser = htmlparser.createParser()
htmlProcesser = processer.createProcesser()
#configWriter = open("config.json", "")

urlManager.pushOne("http://www.jokeji.cn");

def hasForGrabbingUrl():
    '''查看是否有可抓取的URL'''
    return urlManager.hasUrl()

def fetchForGrabbingUrl():
    '''获取待抓取的URL'''
    return urlManager.pop()

def pushNewGrabUrl(urllist):
    '''防止新的待抓取的URL'''
    urlManager.pushList(urllist)

def setGrabbedUrl(url):
    urlManager.setGrabbedUrl(url)

def fetchWebContent(url):
    '''抓取内容'''
    content = downLoader.download(url);
    return content

def parseContent(url, content):
    '''解析抓取的内容'''
    newurl, newdata = htmlParser.parse(url, content)
    logger.debug("newurl : %s" % newurl)
    logger.debug("newdata : %s" % newdata)
    return newurl, newdata

def processContent(data):
    htmlProcesser.process(data)

def writeToFile(name, content):
    f = open(name, mode="w", encoding="utf-8")
    f.write(content)
    f.close()

def grabbing(url):
    '''实际抓取函数'''
    content = None
    try:
        content = fetchWebContent(url)
    except Exception as e:
        logger.debug("e : %s" % e)
    #writeToFile(time.strftime("yyyyMMdd") + ".html", content)
    newurl, newdata = parseContent(url, content)
    setGrabbedUrl(url)
    newList = list(newurl)
    urlManager.pushList(newList)
    processContent(newdata)
    time.sleep(1)

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
    pool = threadpool.ThreadPool(threadNum)
    while RUNNING:
        hasGrabUrl = hasForGrabbingUrl()
        if hasGrabUrl:
            grabUrl = fetchForGrabbingUrl()
            logger.debug("开启抓取任务 leftsize : %d , grabsize : %d , url :%s" % (urlManager.size(), len(urlManager.grabbedList()), grabUrl))
            pool.addJob(grabbing, grabUrl)
        else:
            size= pool.workSize()
            logger.debug("size : %d" % size)
            if (size > 0):
                try:
                    time.sleep(5);
                except:
                    pass
            else:
                logger.debug("抓取完毕，退出循环")
                break;
    logger.debug("等待所有任务退出")
    pool.waitForComplete()

def cleanup():
    global htmlProcesser
    del htmlProcesser

if __name__ == "__main__":
    registerSignal()
    grabWithThreadPool()
    #grabbing("http://www.jokeji.cn/jokehtml/bxnn/2017072923230416.htm")
    cleanup()
    logger.debug("Crawler over, grabbedSize : %s" % len(urlManager.grabbedList()));
