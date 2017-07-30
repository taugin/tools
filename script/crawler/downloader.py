# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import urllib.request;
'''
下载器
'''
class Downloader:
    def __init__(self, url):
        self.url = url;

    def download(self):
        res = urllib.request.urlopen(self.url, None, timeout=10 * 1000);
        charset = self.parseCharset(res);
        logger.debug("charset : %s" % charset)
        content = res.read().decode(charset);
        res.close();
        return content;
    def downloadHttps(self):
        pass
    def parseCharset(self, res):
        contentType = res.getheader("Content-Type")
        charset = "utf-8"
        if contentType != None:
            tmp = contentType.split(";")
            for t in tmp:
                if (t != None and t.startswith("charset")):
                    charset = t.split("=")[1]
        if charset == None or charset.strip() == "":
            charset = "iso-8859-1";
        return charset