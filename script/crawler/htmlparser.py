# coding: UTF-8
# 引入别的文件夹的模块

from commoncfg import logger
import re

import re

from bs4 import BeautifulSoup

from urllib.parse import urljoin

# 实现解析器的类
class HtmlParse(object):
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

    # 解析网页
    def parse(self, page_url, html_content):
        if page_url == None or html_content == None:
            return set(), {}
        # 使用beautifulsoup进行解析
        soup = BeautifulSoup(html_content, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)
        new_data = None#self._get_new_data(page_url, soup)
        return new_urls, new_data