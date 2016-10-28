#coding:utf-8
"""
@file:      LwwSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-26 21:14
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

import re
from bs4 import BeautifulSoup as BS
from crawl_tools.request_with_proxy import request_with_random_ua
from Journals_Task.JournalSpider import JournalSpider
from journal_parser.Lww_Parser import LwwArticle,LwwParser
from multiprocessing.dummy import Pool as ThreadPool

class LwwSpider(JournalSpider):
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def get_volume_link_by_year(self,year):
        volumes_page_url = '{}&year={}'.format(self.url,year)
        print(volumes_page_url)
        volume_page_links = [
            'http://journals.lww.com{}'.format(a['href'])
              for a in BS(request_with_random_ua(volumes_page_url).text,'lxml')\
                    .select_one('#ej-past-issues-detail-list')\
                        .find_all('a',text=re.compile('Volume'))
        ]
        self.volume_links.extend(volume_page_links)

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        self.url = (self.url+'?mobile=0&desktopMode=true')\
            .replace('default','issuelist')
        soup = BS(request_with_random_ua(self.url).text,'lxml')
        years = [
            int(option.text) for option in
                soup.select_one('#ej-article-action-toolbar-select').select('option')
        ]
        pool = ThreadPool(8)
        pool.map(self.get_volume_link_by_year,years)
        pool.close()
        pool.join()

    def run(self,internal_thread_cot=8,just_init=False):
        self._run(
            AllItemsPageParser = LwwParser,
            JournalArticle = LwwArticle,
            internal_thread_cot = internal_thread_cot,
            just_init = just_init,
            debug = False
        )

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://journals.lww.com/nsca-jscr/pages/default.aspx'
    spider = LwwSpider(j)
