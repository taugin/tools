# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import urllib.request
from urllib.parse import quote
import  string

'''
PyQt4 Download地址
https://riverbankcomputing.com/software/pyqt/download
下载器
'''
class Downloader:
    def download(self, url):
        try:
            quotedurl = quote(url, safe = string.printable)
            logger.debug("request start : %s" % url);
            res = urllib.request.urlopen(quotedurl, None, timeout=10 * 1000);
            logger.debug("request  end  : %s" % url);
            content = self.decodeContent(res)
            res.close();
            return content;
        except:
            pass
        return None
    def downloadHttps(self):
        pass
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