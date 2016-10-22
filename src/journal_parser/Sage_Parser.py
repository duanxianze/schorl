#coding:utf-8
"""
@file:      Sage_Parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-21 20:02
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

import re
from bs4 import BeautifulSoup
from journal_parser.JournalArticle import JournalArticle
from crawl_tools.decorators import except_pass
EP_METHOD = lambda func:except_pass(func,'SageArticle')


class SageParser:
    '''
        sample_url: http://tcn.sagepub.com/content/12/2.toc#content-block
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('Sage.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def sections(self):
        return self.soup.select('.toc-cit')


class SageArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title = self.sec.select_one('.cit-title-group').text.strip()

    @EP_METHOD
    def generate_authors(self):
        self.authors = [ author.text for author in self.sec.select('.cit-auth') ]

    @EP_METHOD
    def generate_year(self):
        self.year = int(self.sec.select_one('.cit-print-date').text.strip().split(' ')[-1])

    @EP_METHOD
    def generate_pdf_temp_url(self):
        self.pdf_temp_url = self.JournalObj.site_source[:-1] + self.sec.find("a",text=re.compile("PDF"))['href']

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = self.sec.select_one('.cit-doi').text.strip('doi:')


if __name__=="__main__":
    parser = SageParser(from_web=False)
    secs = parser.sections
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://tcn.sagepub.com/'
    for sec in secs:
        article = SageArticle(sec,j,2)
        article.show_in_cmd()