# -*- coding: utf-8 -*-
"""
@file:      Lww_Parser
@author:    WYn
@contact:   genius_wz@aliyun.com
@python:    2.7.10
@editor:    pyCharm
@create:    2016-10-21 20:02
@description:
            Parser for Lww Publisher
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

import re
from bs4 import BeautifulSoup
from journal_parser.JournalArticle import JournalArticle
from crawl_tools.decorators import except_pass
EP_METHOD = lambda func:except_pass(func,ModelName='LwwArticle')

class LwwParser:
    '''
        http://journals.lww.com/headtraumarehab/pages/currenttoc.aspx
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('./Lww.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'html.parser')

    @property
    def sections(self):
        return self.soup.select('#ej-featured-article')

    @property
    def volume_year(self):
        return int(self.soup.find('span',id=re.compile('DataYear')).text.split(' ')[-1])


class LwwArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id,year):
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()
        self.year = year

    @EP_METHOD
    def generate_title(self):
        self.title = self.sec.select_one('#ej-featured-article-info > h4 > a')['title']

    @EP_METHOD
    def generate_authors(self):
        self.authors = [
            author.replace(',','') for author in
                self.sec.select_one('#paraArticleAuthorshort').text.strip().split(';')
        ]
        if self.authors[-1]=='\xa0More':
            self.authors = self.authors[:-1]

    def generate_pdf_url(self):
        try:
            self.pdf_url=self.sec.select_one('.ejp-standard-pdf')['href']
        except:
            pass

    @EP_METHOD
    def generate_id_by_journal(self):
        a=self.sec.select_one('#paraArticleCitation').text
        self.id_by_journal=re.split('\.|\,',a)[1]

    @EP_METHOD
    def generate_link(self):
        self.link = self.sec.select_one('#ej-featured-article-info > h4 > a')['href']


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    journal = Journal()
    for sec in LwwParser(from_web=False).sections:
        article = LwwArticle(sec,journal,2,1988)
        article.show_in_cmd()