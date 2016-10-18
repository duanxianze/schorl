#coding:utf-8
"""
@file:      TaylorFrancisSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-01 3:52
@description:
            --
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from journal_parser.TaylorFrancis_Parser import TaylorFrancisArticle,TaylorFrancisParser
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua
import requests,re
from bs4 import BeautifulSoup as BS


class TaylorFrancisSpider(JournalSpider):
    '''
        sample url:http://www.tandfonline.com/toc/ghbi20/current
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.JournalObj = JournalObj
        self.url = JournalObj.site_source
        self.handle_taylor_url()
        self.generate_volume_links()

    '''
    #法一，到专门的volume_link集合页寻找，需要记录session区间，已被淘汰
    def handle_taylor_url(self):
        journal_id = self.url.split('/')[-2]
        self.url = 'http://www.tandfonline.com/loi/{}'.format(journal_id)
        print(self.url)

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        with requests.Session() as s:
            for url in list(map(
                lambda x:'http://www.tandfonline.com'+x['href'],
                BS(requests.get(self.url).text,'lxml')\
                        .find_all(class_='volume_link')
            )):
                resp = s.get(url)
        self.volume_links = list(map(
            lambda x:'http://www.tandfonline.com'+x['href'],
            BS(resp.text,'lxml').find_all(
                href = re.compile("nav=tocList")
            )
        ))
    '''
    def handle_taylor_url(self):
        #先指current卷页面，volume_link信息每页都有
        pass

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        self.volume_links = TaylorFrancisParser(
            html_source=request_with_random_ua(self.url).text
        ).volume_links

    def run(self,internal_thread_cot=8):
        self._run(
            AllItemsPageParser = TaylorFrancisParser,
            JournalArticle = TaylorFrancisArticle,
            internal_thread_cot=internal_thread_cot,
            use_tor = True
        )


