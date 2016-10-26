#coding:utf-8
"""
@file:         Acs_Parser.py
@author:       yaotong
@contact:      569493458@qq.com
@python:       3.5.2
@editor:       pycharm
@create:       2016-10-24 18:51
@description:
           Parser for Acs Publisher
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
EP_METHOD = lambda func:except_pass(func,ModelName='AcsArticle')


class AcsParser:
    '''
        #sample_url:  http://pubs.acs.org/toc/mpohbp/0/0
    '''
    def __init__(self, html_source = None, from_web = True):
        if not from_web:
            with open("./pages/Acs.html", "rb") as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source, 'lxml')

    @property
    def sections(self):
        return self.soup.select('.articleBox')

    @property
    def volume_year(self):
        return int(self.soup.select_one('#date').text.split(' ')[-1].strip())


class AcsArticle(JournalArticle):
    def __init__(self, sec, JournalObj,volume_db_id,year):
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()
        self.year = year

    @EP_METHOD
    def generate_title(self):
        self.title = self.sec.select_one('.art_title').text.strip()

    @EP_METHOD
    def generate_authors(self):
        self.authors = [ author.text for author in self.sec.select('.entryAuthor')]

    @EP_METHOD
    def generate_pdf_temp_url(self):
        self.pdf_temp_url = 'http://pubs.acs.org'+self.sec.find(
            "a",title = re.compile("Download the PDF Full Text")
        )['href']

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = self.sec.select_one('.DOI').text.strip('DOI:')

    @EP_METHOD
    def generate_link(self):
        self.link = 'http://pubs.acs.org'\
            +self.sec.select_one('.art_title > a')['href']

if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    acs = Journal()
    for sec in AcsParser(from_web=False).sections:
        article = AcsArticle(sec,acs,2)
        article.show_in_cmd()




















