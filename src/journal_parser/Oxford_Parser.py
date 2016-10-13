#coding:utf-8
"""
@file:      Oxford_Parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-13 20:06
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
from journal_parser.JournalArticle import JournalArticle
from crawl_tools.request_with_proxy import request_with_random_ua
from bs4 import BeautifulSoup
import re


class OxfordAllItemsPageParser:
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('Oxford.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def sections(self):
        return self.soup.select_one('#content-block').select('.toc-level')

    @property
    def volume_year(self):
        return int(self.soup.select_one('.toc-top-pub-date').text.strip().split(' ')[-1])


class OxfordArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.unit = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    def generate_title(self):
        self.title = self.unit.select_one('span').text

    def generate_authors(self):
        self.authors = list(map(
            lambda x:x.text,
            self.unit.select('.cit-auth-type-author')
        ))

    def generate_link(self):
        pass

    def generate_abstract(self):
        pass

    def generate_year(self):
        pass

    def generate_pdf_url(self):
        pass

    def generate_pdf_temp_url(self):
        pass

    def generate_id_by_journal(self):
        pass

if __name__=="__main__":
    oa = OxfordAllItemsPageParser(from_web=False)
    print(len(oa.sections))
    print(oa.volume_year)
    from Journals_Task.JournalClass import Journal
    for sec in oa.sections:
        OxfordArticle(sec,Journal(),2).show_in_cmd()