# coding: UTF-8
# 引入别的文件夹的模块

import pathconfig
import Common
import logger
import Utils
import urllib.request;
'''
下载器
'''
class Downloader:
    def __init__(self, url):
        self.url = url;

    def download(self):
        res = urllib.request.urlopen(self.url, None, timeout=10 * 1000);
        content = res.read().decode('utf-8');
        res.close();
        return content;
    def downloadHttps(self):
        pass

downloader = Downloader("https://www.baidu.com");
content = downloader.download();
