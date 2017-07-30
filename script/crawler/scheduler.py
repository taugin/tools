# coding: UTF-8
# 引入别的文件夹的模块

import Common
import Utils
import urlmanager
import threading
from commoncfg import logger
import downloader
import htmlparser
import time

threadNum = 5
condition = threading.Condition()
urlManager = urlmanager.UrlManager()

#urlManager.pushOne("http://www.baidu.com");
#urlManager.pushOne("http://www.xiaonei.com");
#urlManager.pushOne("http://www.126.com");
urlManager.pushOne("http://www.csdn.com");
#urlManager.pushOne("http://www.jokeji.cn/JokeHtml/mj/201707292319522.htm");

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
    down = downloader.Downloader(url)
    content = down.download();
    return content

def parseContent(url, content):
    '''解析抓取的内容'''
    parser = htmlparser.HtmlParse()
    newurl, newdata = parser.parse(url, content)
    return newurl, newdata

class GrabThread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        content = None
        try:
            content = fetchWebContent(self.url)
        except Exception as e:
            logger.debug("e : %s" % e)

        '''
        f = open(self.name + ".html", mode="w", encoding="utf-8")
        f.write(content)
        f.close()
        '''
        newurl, newdata = parseContent(self.url, content)
        setGrabbedUrl(self.url)
        newList = list(newurl)
        urlManager.pushList(newList)
        logger.debug(self.name + " over")
        time.sleep(2)
        #工作线程结束，通知主线程
        if condition.acquire():
            condition.notify()
            condition.release()

if __name__ == "__main__":
    threadList = []
    while True:
        continueGrab = hasForGrabbingUrl()
        if continueGrab:
            activeCount = threading.activeCount()
            if activeCount < threadNum + 1:
                grabUrl = fetchForGrabbingUrl()
                logger.debug("开启抓取线程 leftsize : %d , grabsize : %d , url :%s" % (urlManager.size(), len(urlManager.grabbedList()), grabUrl))
                t = GrabThread(grabUrl)
                threadList.append(t)
                t.start()
            else:
                #logger.debug("等待有线程运行结束")
                if condition.acquire():
                    condition.wait();
                    condition.release()
        else:
            activeCount = threading.activeCount()
            logger.debug("未找到抓取URL activeCount : %d" % activeCount)
            if activeCount > 1:
                time.sleep(5);
            else:
                logger.debug("抓取完毕，退出循环")
                break;
    logger.debug("Crawler over, grabbedSize : %s" % len(urlManager.grabbedList()));
