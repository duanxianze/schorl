#coding:utf-8
"""
@file:      BiomedSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-13 21:36
@description:
            sample_url: http://www.biomedcentral.com/bmcfampract/
"""

import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

import requests,time,random
from Journals_Task.JournalSpider import JournalSpider
from journal_parser.Biomed_Parser import BioMedParser,BioMedArticle
from crawl_tools.request_with_proxy import request_with_random_ua
from bs4 import BeautifulSoup

class BioMedSpider(JournalSpider):
    '''
        Sample Url:
            http://www.biomedcentral.com/bmcbioinformatics/
            http://www.biomedcentral.com/bmcplantbiol/
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        name = self.url[:-1].split('/')[-1]
        items_fist_page_url = 'http://{}.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page=1'.format(name)
        print(items_fist_page_url)
        pages_num = BioMedParser(
            html_source = request_with_random_ua(
                url=items_fist_page_url,timeout=3).text
        ).pages_amount
        for i in range(1,pages_num+1):
            page_url = 'http://{}.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page={}'\
                .format(name,i)
            self.volume_links.append(page_url)


    def run(self,internal_thread_cot=8):
        self._run(
            AllItemsPageParser = BioMedParser,
            JournalArticle = BioMedArticle,
            internal_thread_cot=internal_thread_cot
        )

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://www.biomedcentral.com/bmcbioinformatics/'
    BioMedSpider(j)