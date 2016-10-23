#coding:utf-8
"""
@file:      WileySpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-23 9:15
@description:
            for wiley
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from bs4 import BeautifulSoup
from Journals_Task.JournalSpider import JournalSpider
from crawl_tools.request_with_proxy import request_with_random_ua
from journal_parser.Wiley_Parser import WileyArticle,WileyAllItemsPageParser
from multiprocessing.dummy import Pool as ThreadPool
import time,re

class WileySpider(JournalSpider):
    '''
	    db_sample_url: http://www3.interscience.wiley.com/journal/33822/home
	'''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def generate_volume_links(self):
        if self.JournalObj.volume_links_got:
            return
        self.volumes_page_url = 'http://onlinelibrary.wiley.com'+BeautifulSoup(
            request_with_random_ua(self.url).text,'lxml'
        ).find('a',text='See all')['href']
        #self.volumes_page_url = 'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1096-987X/issues'
        soup = BeautifulSoup(
            request_with_random_ua(self.volumes_page_url).text,'lxml'
        )
        years = [
            int(a['href'].split('=')[-1]) for a in
                soup.find_all('a',id=re.compile('year_[0-9]+_link'))
        ]
        pool = ThreadPool(16)
        pool.map(self.get_volume_links_by_year,years)
        pool.close()
        pool.join()

    def get_volume_links_by_year(self,year):
        ajax_url = '{}/fragment?activeYear={}&SKIP_DECORATION=true'\
            .format(self.volumes_page_url,year)
        for i in range(5):
            a_list = BeautifulSoup(
                request_with_random_ua(ajax_url).text,'lxml'
            ).select('.issue > a')
            if a_list:
                break
        volume_links_by_year = [ 'http://onlinelibrary.wiley.com'+a['href'] for a in a_list ]
        if volume_links_by_year==[]:
            print('error ajax_url:{}'.format(ajax_url))
        self.volume_links.extend(volume_links_by_year)

    def run(self,internal_thread_cot=8,just_init=False):
        self._run(
            AllItemsPageParser = WileyAllItemsPageParser,
            JournalArticle = WileyArticle,
            check_pdf_url=False,
            just_init = just_init,
            internal_thread_cot=internal_thread_cot
        )

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://www3.interscience.wiley.com/journal/33822/home'
    spider = WileySpider(j)
