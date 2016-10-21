#coding:utf-8
"""
@file:      SageSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-21 20:01
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

import requests,time
from Journals_Task.JournalSpider import JournalSpider
from journal_parser.Sage_Parser import SageParser,SageArticle
from crawl_tools.request_with_proxy import request_with_random_ua
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

class SageSpider(JournalSpider):
    '''
        sample_url:     http://jsw.sagepub.com/
        因为做了响应式，这里全部用Samsung S5 的 user agent
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def get_volume_links_by_year(self,url):
        print(url)
        soup = BeautifulSoup(
            requests.get(url,
                headers = {
                    'user-agent':'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'
                }
            ).text,'lxml'
        )
        volume_links = [ self.JournalObj.site_source[:-1]+a['href'] for a in soup.select('.article-title > a') ]
        print(volume_links)
        self.volume_links.extend(volume_links)

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        soup = BeautifulSoup(
            requests.get(
                url = self.url + 'content/by/year',
                headers = {
                    'user-agent':'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'
                }
            ).text,'lxml'
        )
        urls = [
            self.JournalObj.site_source[:-1]+a['href']
                for a in list(set(soup.select_one('.pane-archive-list')\
                        .select_one('.item-list').select('a')))
        ]
        print(urls)
        pool = ThreadPool(16)
        pool.map(self.get_volume_links_by_year,urls)
        pool.close()
        pool.join()

    def run(self,internal_thread_cot=8):
        self._run(
            AllItemsPageParser = SageParser,
            JournalArticle = SageArticle,
            internal_thread_cot=internal_thread_cot
        )

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://tcn.sagepub.com/'
    SageSpider(j)
