# coding: UTF-8
# 引入别的文件夹的模块
'''
BeautifulSoup下载地址
https://pypi.python.org/pypi/beautifulsoup4/4.3.2
https://pypi.python.org/packages/30/bd/5405ba01391d06646de9ec90cadeb3893fa355a06438966afff44531219a/beautifulsoup4-4.3.2.tar.gz
'''
from commoncfg import logger
import re

from bs4 import BeautifulSoup

from urllib.parse import urljoin
from urllib.parse import urlparse
import time
import hashlib

topHostPostfix = (
    '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
    '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
    '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
    '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
    '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
    '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
    '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
    '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
    '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
    '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
    '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk", ".cn")

regx = r'[^\.]+(' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
pattern = re.compile(regx, re.IGNORECASE)

def parseDomainName(url):
    parts = urlparse(url)
    host = parts.netloc
    m = pattern.search(host)
    return m.group() if m else None

def createParser(url):
    domain = parseDomainName(url)
    logger.debug("domain : %s" % domain)
    htmlParse = None
    if domain == "xiao688.com":
        htmlParse = Xiao688HtmlParser()
    elif domain == "jokeji.cn":
        htmlParse = JokejiHtmlParser()
    else:
        htmlParse = None
    if htmlParse != None:
        htmlParse.setDomain(domain)
    return htmlParse

# 实现解析器的类
class HtmlParse(object):
    def setDomain(self, domain):
        self.domain = domain
    # 解析网页
    def parse(self, page_url, html_content):
        if page_url == None or html_content == None:
            return set(), None
        # 使用beautifulsoup进行解析
        soup = BeautifulSoup(html_content, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data

    # 从网页解析中获得url
    def _get_new_urls(self, page_url, soup):
        new_urls = set()
        # 匹配/view/123.htm形式的url，得到所有的词条url
        links = None
        try:
            links = soup.find_all("a", href=re.compile(r".*?\.htm"))
        except:
            pass
        if links != None:
            for link in links:
                new_url = link['href']
                new_full_url = urljoin(page_url, new_url)
                if new_full_url.find(self.domain) > -1:
                    new_urls.add(new_full_url)
        return new_urls

    # 从网页解析中获得数据
    def _get_new_data(self, page_url, soup):
        return None

class JokejiHtmlParser(HtmlParse):
    def __init__(self):
        pass

    def _formatTime(self, pub_time):
        try:
            timeArray = time.strptime(pub_time, "%Y/%m/%d %H:%M:%S")
            return int(time.mktime(timeArray))
        except:
            return int(time.time())

    def _get_new_data(self, page_url, soup):
        res_data = {}

        datacontent = None
        pubTimestamp = int(time.time())
        title = None
        pageurl = page_url

        try:
            allJokeNode = soup.find("span", id="text110")
            if allJokeNode != None:
                datacontent = str(allJokeNode)
            else:
                datacontent = None
            if datacontent != None:
                title = soup.title.get_text().strip()
                allLiNode = soup.find("div", class_="pl_ad").find("ul").find_all("li")
                pub_time = allLiNode[2].find("i").get_text().strip()[5:]
                pubTimestamp = self._formatTime(pub_time)
        except Exception as e:
            logger.debug("error : %s" % e)

        if datacontent == None:
            try:
                allJokeNode = soup.find("div", class_="txt")
                if allJokeNode != None:
                    cNode = allJokeNode.find("ul")
                    if cNode != None:
                        datacontent = str(cNode)
                    else:
                        datacontent = None
                    if datacontent != None:
                        title = allJokeNode.find("h1").get_text()
                        timeStr = allJokeNode.find("b").get_text()
                        reg = r"([1-9]\d{3}/([1-9]|1[0-2])/([1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d)";
                        pattern = re.compile(reg, re.IGNORECASE)
                        m = pattern.search(timeStr)
                        pub_time = m.group() if m else None
                        pubTimestamp = self._formatTime(pub_time)
                else:
                    datacontent = None
            except Exception as e:
                logger.debug("error : %s" % e)

        if datacontent != None:
            datacontent = datacontent.replace("'", "\\'")
            res_data['title'] = title
            res_data['pubtime'] = pubTimestamp
            res_data['content'] = datacontent
            res_data['pageurl'] = pageurl
            res_data['urlmd5'] = hashlib.md5(pageurl.encode('utf-8')).hexdigest()
            return res_data
        return None

class Xiao688HtmlParser(HtmlParse):
    def __init__(self):
        pass

    def _get_new_data(self, page_url, soup):
        res_data = {}

        datacontent = None
        pubTimestamp = int(time.time())
        title = None
        pageurl = page_url

        try:
            allJokeNode = soup.find("div", class_="content")
            if allJokeNode != None:
                datacontent = str(allJokeNode)
            else:
                datacontent = None
            if datacontent != None:
                titleNode = soup.find("div", class_="title").find("h1")
                title = titleNode.get_text().strip()
        except Exception as e:
            logger.debug("e : %s" % e)

        try:
            pubTimeNode = soup.find("span", id="d_udate")
            pub_time = pubTimeNode.get_text().strip()[1:-1]
            timeArray = time.strptime(pub_time, "%Y-%m-%d %H:%M")
            pubTimestamp = int(time.mktime(timeArray))
        except:
            pubTimestamp = int(time.time())

        if datacontent != None:
            datacontent = datacontent.replace("'", "\\'")
            res_data['title'] = title
            res_data['pubtime'] = pubTimestamp
            res_data['content'] = datacontent
            res_data['pageurl'] = pageurl
            res_data['urlmd5'] = hashlib.md5(pageurl.encode('utf-8')).hexdigest()
            return res_data
        return None
