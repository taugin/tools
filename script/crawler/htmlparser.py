# coding: UTF-8
# 引入别的文件夹的模块
'''
BeautifulSoup下载地址
https://pypi.python.org/pypi/beautifulsoup4/4.3.2
https://pypi.python.org/packages/30/bd/5405ba01391d06646de9ec90cadeb3893fa355a06438966afff44531219a/beautifulsoup4-4.3.2.tar.gz
'''
from commoncfg import logger
import re

import re

from bs4 import BeautifulSoup

from urllib.parse import urljoin


def createParser():
    return Xiao688HtmlParser()

# 实现解析器的类
class HtmlParse(object):
    # 解析网页
    def parse(self, page_url, html_content):
        if page_url == None or html_content == None:
            return set(), {}
        # 使用beautifulsoup进行解析
        soup = BeautifulSoup(html_content, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        if new_urls == None:
            new_urls = set()
        if new_data == None:
            new_data = {}
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
                new_urls.add(new_full_url)
        return new_urls

    # 从网页解析中获得数据
    def _get_new_data(self, page_url, soup):
        # 存储数据的字典
        res_data = {}

        # 根据页面的特征，获取标题内容
        title_node = soup.find("span", id="text110").find("p")
        title = title_node.get_text()

        # 根据页面的特征，获取摘要内容
        summary_node = soup.find('div', class_="lemma-summary")
        if summary_node is None:
            summary = "None summary"
        else:
            summary = summary_node.get_text()

        # 保存网页的内容
        res_data['url'] = page_url
        res_data['title'] = title
        res_data['summary'] = summary

class JDHtmlParser(HtmlParse):
    def __init__(self):
        pass

    def _get_new_data(self, page_url, soup):
        res_data = {}
        title_node = soup.find("h3", class_="tb-main-title")
        title = title_node.get_text().strip()
        print(title)
        price_node = soup.find("em", class_="tb-rmb-num")
        price = price_node.get_text().strip()
        print(price)
        desc_node = soup.find("p", class_="tb-subtitle")
        desc = desc_node.get_text().strip()
        print(desc)

class JokejiHtmlParser(HtmlParse):
    def __init__(self):
        pass

    def _get_new_data(self, page_url, soup):
        import time
        res_data = {}
        data_list = []
        pub_time = None
        allJokeNode = None
        pub_timestamp = None
        try:
            allJokeNode = soup.find("span", id="text110").find_all("p")
        except:
            pass

        if allJokeNode != None:
            for node in allJokeNode:
                data_list.append(node.get_text().strip())

        try:
            allLiNode = soup.find("div", class_="pl_ad").find("ul").find_all("li")
            pub_time = allLiNode[2].find("i").get_text().strip()[5:]
        except:
            pub_time = 0

        try:
            timeArray = time.strptime(pub_time, "%Y/%m/%d %H:%M:%S")
            pub_timestamp = int(time.mktime(timeArray))
        except:
            pub_timestamp = int(time.time())

        if data_list != None and len(data_list) > 0:
            res_data['title'] = soup.title.get_text().strip()
            res_data['pubtime'] = pub_timestamp
            res_data['content'] = data_list
            res_data['pageurl'] = page_url
            return res_data
        return None
class Xiao688HtmlParser(HtmlParse):
    def __init__(self):
        pass

    def _get_new_data(self, page_url, soup):
        import time
        res_data = {}

        datacontent = None
        pubTimestamp = None
        title = None
        pageurl = page_url

        #获取标题
        try:
            titleNode = soup.find("div", class_="title").find("h1")
            title = titleNode.get_text().strip()
        except:
            pass
        #获取内容
        try:
            allJokeNode = soup.find("div", class_="content")
            datacontent = str(allJokeNode)
        except Exception as e:
            logger.debug("error : %s" % e)

        try:
            pubTimeNode = soup.find("span", id="d_udate")
            pub_time = pubTimeNode.get_text().strip()[1:-1]
            timeArray = time.strptime(pub_time, "%Y-%m-%d %H:%M")
            pubTimestamp = int(time.mktime(timeArray))
        except:
            pubTimestamp = int(time.time())

        if datacontent != None:
            datacontent = datacontent.replace("'", "\'")
            res_data['title'] = title
            res_data['pubtime'] = pubTimestamp
            res_data['content'] = datacontent
            res_data['pageurl'] = pageurl
            return res_data
        return None