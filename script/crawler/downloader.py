# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import urllib.request;

'''
PyQt4 Download地址
https://riverbankcomputing.com/software/pyqt/download
下载器
'''
class Downloader:
    def download(self, url):
        res = urllib.request.urlopen(url, None, timeout=10 * 1000);
        charset = self.parseCharset(res);
        logger.debug("charset : %s" % charset)
        resbytes = res.read()
        content = resbytes.decode(charset);
        res.close();
        return content;
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