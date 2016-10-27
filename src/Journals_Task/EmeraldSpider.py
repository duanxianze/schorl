#coding:utf-8
"""
@file:      EmeraldSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/10/28 04:32
@description:
            Spider Module For Emerald Publisher
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from bs4 import BeautifulSoup as BS
from crawl_tools.request_with_proxy import request_with_random_ua
from Journals_Task.JournalSpider import JournalSpider
from journal_parser.Emerald_Parser import EmeraldParser,EmeraldArticle

class EmeraldSpider(JournalSpider):
    '''
        sample_url: http://www.emeraldgrouppublishing.com/products/journals/journals.htm?id=f
    '''
    def __init__(self,JournalObj):
        JournalSpider.__init__(self,JournalObj)
        self.url = JournalObj.site_source
        self.JournalObj = JournalObj
        self.generate_volume_links()

    def generate_volume_links(self):
        id = self.url.split('id=')[-1]
        volumes_page_link = 'http://www.emeraldinsight.com/loi/{}'.format(id)
        for i in range(10):
            resp = request_with_random_ua(
                url=volumes_page_link,timeout=10)
            soup = BS(resp.text,'lxml')
            self.volume_links = [ a['href'] for a in soup.select('.tocIssueLink') ]
            if self.volume_links!=[]:
                break

    def run(self,internal_thread_cot=8,just_init=False):
        self._run(
            AllItemsPageParser = EmeraldParser,
            JournalArticle = EmeraldArticle,
            internal_thread_cot = internal_thread_cot,
            just_init = just_init,
            debug=True
        )

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://www.emeraldgrouppublishing.com/products/journals/journals.htm?id=f'
    spider = EmeraldSpider(j)