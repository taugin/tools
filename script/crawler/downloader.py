# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import urllib.request
from urllib.parse import quote
import  string
from http.cookiejar import CookieJar
import random

'''
PyQt4 Download地址
https://riverbankcomputing.com/software/pyqt/download
下载器
'''
userAgent = [
             "mozilla/5.0 (windows nt 6.1; wow64) applewebkit/537.36 (khtml, like gecko) chrome/45.0.2454.101 safari/537.36",
             "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6",
             "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13"
             ]
class Downloader:
    def __init__(self):
        self.headers = {"User-Agent" : userAgent[round(random.random() * (len(userAgent) - 1))]}
        self.data = None
        self.httpAuth = None
        self.proxies = None
        self.proxyAuth = None
        self.cookie = None
        pass

    def download(self, url):
        try:
            quotedurl = quote(url, safe=string.printable)
            logger.debug("request start : %s" % url);
            req = urllib.request.Request(quotedurl)
            #添加Header
            self.addHeaders(req)
            #添加opener
            urllib.request.install_opener(self.buildOpener())
            #执行请求
            logger.debug("headers : %s" % req.headers)
            data = self.getReqData()
            logger.debug("data : %s" % data)
            res = urllib.request.urlopen(req, data = data, timeout=self.getTimeout());
            logger.debug("request  end  : %s" % url);
            #解析内容
            content = self.decodeContent(res)
            res.close();
            return content;
        except Exception as e:
            logger.debug("error : %s" % e)
        return None

    def addHeaders(self, req):
        if self.headers != None:
            for name in self.headers :
                req.add_header(name, self.headers[name])

    def getTimeout(self):
        return 10 * 1000

    def getReqData(self):
        try:
            if self.data != None:
                return urllib.parse.urlencode(self.data).encode(encoding='utf_8', errors='strict')
            return None
        except:
            return None

    def buildOpener(self):
        handlers = []
        authHandler = self.buildAuthHandler()
        if authHandler != None:
            handlers.append(authHandler)

        proxyHandler, proxyAuthHandler = self.buildProxyHandler()
        if proxyHandler != None and proxyAuthHandler != None:
            handlers.append(proxyHandler)
            handlers.append(proxyAuthHandler)

        cookieHandler = self.buildCookieHandler()
        if cookieHandler != None:
            handlers.append(cookieHandler)

        #增加重定向处理器，此处禁止重定向
        redirectHandler = self.buildRedirectHandler()
        if redirectHandler != None:
            handlers.append(redirectHandler)

        opener = urllib.request.build_opener(*handlers)
        return opener

    def buildAuthHandler(self):
        if self.httpAuth == None:
            return None
        try:
            auth = {
                    "realm" : "Tomcat Manager Application",
                    "uri" : "http://106.14.185.49:8080/manager/html",
                    "user" : "taugin",
                    "passwd" : "taugin0426"
            }
            auth_handler = urllib.request.HTTPBasicAuthHandler()
            auth_handler.add_password(realm=self.httpAuth["realm"],
                              uri=self.httpAuth["uri"],
                              user=self.httpAuth["user"],
                              passwd=self.httpAuth["passwd"])
            return auth_handler
        except Exception as e:
            logger.debug("error : " +e)
        return None

    def buildProxyHandler(self):
        if self.proxies == None or self.proxyAuth == None:
            return None, None
        try:
            proxies = {'http': 'http://www.example.com:3128/'}
            auth = {
                    "realm" : "realm",
                    "uri" : "uri",
                    "user" : "user",
                    "passwd" : "passwd"
            }
            proxy_handler = urllib.request.ProxyHandler(self.proxies)
            proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()
            proxy_auth_handler.add_password(self.proxyAuth['realm'], self.proxyAuth['uri'], self.proxyAuth['user'], self.proxyAuth['passwd'])
            return proxy_handler, proxy_auth_handler
        except Exception as e:
            logger.debug("error : %s" % e)
        return None, None

    def buildCookieHandler(self):
        try:
            self.cookie = CookieJar()
            return urllib.request.HTTPCookieProcessor(self.cookie)
        except Exception as e:
            logger.debug("error : %s" % e)
        return None

    def buildRedirectHandler(self):
        try:
            return RedirectHandler()
        except Exception as e:
            logger.debug("error : %s" % e)
        return None

    def parseCharset(self, res):
        contentType = res.getheader("Content-Type")
        charset = None
        if contentType != None:
            tmp = contentType.split(";")
            for t in tmp:
                if (t != None and t.strip().find("charset") > -1):
                    charset = t.split("=")[1]
        if charset == None or charset.strip() == "":
            charset = "GB18030";
        return charset
    def decodeContent(self, res):
        charset = self.parseCharset(res);
        resbytes = res.read()
        try:
            content = resbytes.decode(charset);
        except:
            content = resbytes.decode("GBK");
        return content

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        pass