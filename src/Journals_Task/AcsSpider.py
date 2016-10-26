#coding:utf-8
"""
@file:      AcsSpider.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-25 20:38
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

from Journals_Task.JournalSpider import JournalSpider
from journal_parser.Acs_Parser import AcsArticle,AcsParser
from crawl_tools.request_with_proxy import request_with_random_ua
from bs4 import BeautifulSoup


class AcsSpider(JournalSpider):
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def generate_volume_links(self):
        #http://pubs.acs.org/journal/ancac3
        if self.JournalObj.volume_links_got:
            return
        index = self.url.split('/')[-1]
        volumes_page_url = 'http://pubs.acs.org/loi/{}'.format(index)
        #print(volumes_page_url)
        a_list = BeautifulSoup(
            request_with_random_ua(volumes_page_url).text,'lxml'
        ).select('.publicationTitle')
        for i in range(20):
            self.volume_links = [
                a['href'] for a in
                    BeautifulSoup(
                        request_with_random_ua(volumes_page_url).text, 'lxml'
                    ).select('.publicationTitle')
            ]
            print(self.volume_links)
            if self.volume_links:
                print('length:',len(self.volume_links))
                break

    def run(self,internal_thread_cot=8,just_init=False,debug=False):
        self._run(
            AllItemsPageParser=AcsParser,
            JournalArticle=AcsArticle,
            internal_thread_cot=internal_thread_cot,
            just_init=just_init,
            debug=True
        )

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://pubs.acs.org/journal/ancac3'
    AcsSpider(j)