#coding:utf-8
"""
@file:      TaylorFrancis_Parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-01 3:46
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

import re,requests
from bs4 import BeautifulSoup
from journal_parser.JournalArticle import JournalArticle
from crawl_tools.decorators import except_pass,except_return_none
ERN_METHOD = lambda func:except_return_none(func,'TaylorFrancisParser')
EP_METHOD = lambda func:except_pass(func,'TaylorFrancisArticle')


class TF_DetailPageParser:
    '''
        http://www.tandfonline.com/doi/abs/10.1080/08912968809386468
    '''
    def __init__(self,url):
        self.soup = BeautifulSoup(
            requests.get('http://www.tandfonline.com/doi/abs/10.1080/08912968809386468').text,
            'lxml'
           )

class TaylorFrancisParser:
    '''

        sample_url: http://www.tandfonline.com/toc/ghbi20/28/8?nav=tocList
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('TaylorFrancis.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    @ERN_METHOD
    def sections(self):
        return self.soup.select('.tocArticleEntry')

    @property
    @ERN_METHOD
    def volume_links(self):
        return list(map(
            lambda x:'http://www.tandfonline.com'+x['href'],
            self.soup.find_all(href=re.compile("nav=tocList"))
        ))

class TaylorFrancisArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @property
    @ERN_METHOD
    def access_get(self):
        return self.sec.select_one('.access-icon')

    @EP_METHOD
    def generate_title(self):
        self.title = self.sec.select_one('.art_title > a > span').text

    @EP_METHOD
    def generate_authors(self):
        self.authors = list(map(
            lambda x:x.text,
            self.sec.select('.articleEntryAuthorsLinks > span > a')
        ))

    @EP_METHOD
    def generate_link(self):
        self.link = 'http://www.tandfonline.com'+self.sec.select_one('.art_title > a')['href']

    @EP_METHOD
    def generate_abstract(self):
        pass

    @EP_METHOD
    def generate_year(self):
        self.year = int(self.sec.select_one('.tocEPubDate').text.split(' ')[-1])

    @EP_METHOD
    def generate_pdf_temp_url(self):
        if self.access_get:
            self.pdf_temp_url = 'tf_open'
        else:
            self.pdf_temp_url = 'tf_close'

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = 'TF'+self.sec.select_one('.art_title > a')['href'].split('/')[-1]

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    JournalObj = Journal()
    JournalObj.site_source = 'http://www.tandfonline.com/toc/ghbi20/current'
    JournalObj.sjr_id = 123
    for sec in TaylorFrancisParser(from_web=False).sections:
        TaylorFrancisArticle(sec,JournalObj,2).show_in_cmd()
