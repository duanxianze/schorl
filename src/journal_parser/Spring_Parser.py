#coding:utf-8
"""
@file:      Spring_Parser.py
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

from bs4 import BeautifulSoup
from journal_parser.JournalArticle import JournalArticle
from crawl_tools.decorators import except_pass
EP_METHOD = lambda func:except_pass(func,'SpringArticle')


class SpringParser:
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('Spring.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def pages_amount(self):
        return int(self.soup.select_one('.number-of-pages')
                   .text.replace(",",""))

    @property
    def sections(self):
        return self.soup.select_one('#results-list').select('li')


class SpringArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title = self.sec.select_one('.title').text

    @EP_METHOD
    def generate_authors(self):
        self.authors = list(map(lambda x:x.text,self.sec.select_one('.authors').select('a')))

    @EP_METHOD
    def generate_link(self):
        self.link = 'http://link.springer.com' + self.sec.select_one('.title')['href']

    @EP_METHOD
    def generate_abstract(self):
        self.abstract = self.sec.select_one('.snippet').text

    @EP_METHOD
    def generate_year(self):
        self.year = int(self.sec.select_one('.year').text[1:-1])

    @EP_METHOD
    def generate_pdf_url(self):
        self.pdf_url = 'http://link.springer.com'+self.sec.select_one('.pdf-link')['href']

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = self.link.split('/')[-1]


