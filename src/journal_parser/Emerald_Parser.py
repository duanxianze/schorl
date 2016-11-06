#coding:utf-8
"""
@file:      Emerald_Parser
@author:    yjh
@contact:
@python:    3.4
@editor:    PyCharm
@create:    2016-10
@description:
            Parser for Emerald Publisher
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
EP_METHOD = lambda func:except_pass(func,ModelName='EmeraldArticle')

class EmeraldParser:
    '''
        sample_url: http://www.emeraldinsight.com/toc/f/32/9%2F10
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('./emerald.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source, 'lxml')

    @property
    def sections(self):
        return self.soup.find_all(class_ = 'articleEntry')

    @property
    def volume_year(self):
        year_str = self.soup.find('span',text=re.compile('Published')).text.strip()
        return int(re.split(',| ',year_str)[1])

class EmeraldArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        self.domain = 'http://www.emeraldinsight.com'
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title =  self.sec.find(class_ = 'art_title').text.strip()

    @EP_METHOD
    def generate_authors(self):
        self.authors = [ author.text.strip() for author in self.sec.find_all(class_ = "entryAuthor")]

    @EP_METHOD
    def generate_id_by_journal(self):
        self.generate_link()
        self.id_by_journal = self.link.strip(self.domain+'/doi/full')

    @EP_METHOD
    def generate_link(self):
        self.link = self.domain + self.sec.find("a",text=re.compile("HTML"))['href']

    @EP_METHOD
    def generate_pdf_temp_url(self):
        self.pdf_temp_url = self.domain + self.sec.find("a",text=re.compile("PDF"))['href']


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    journal = Journal()
    parser = EmeraldParser(from_web=False)
    year = parser.volume_year
    for sec in parser.sections:
        article = EmeraldArticle(sec,journal,2)
        article.show_in_cmd()
    print(year)