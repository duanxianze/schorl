#coding:utf-8
"""
@file:      IEEE_Spider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:55
@description:
            ??
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from Journals_Task.JournalSpider import JournalSpider
from journal_parser.IEEE_Parser import IEEE_AllItemsPageParser,IEEE_Article
from crawl_tools.request_with_proxy import request_with_random_ua
import psycopg2,time

class IEEE_Spider(JournalSpider):
    '''
       sample_url: http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        #假如数据库中已保存，直接读取即可，无需生成
        self.volume_links = IEEE_AllItemsPageParser(
            html_source = request_with_random_ua(self.url).text
        ).volume_links

    def handle_volume_link_for_multi_results(self,volume_link):
        return volume_link+'&rowsPerPage=500&pageNumber=1'

    def run(self):
        self._run(
            AllItemsPageParser = IEEE_AllItemsPageParser,
            JournalArticle = IEEE_Article
        )
