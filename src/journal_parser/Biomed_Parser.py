#coding:utf-8
"""
@file:      Biomed_Parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-10-13 21:37
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
EP_METHOD = lambda func:except_pass(func,'BioMedArticle')

class BioMedParser:
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('BioMed.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def pages_amount(self):
        return int(self.soup.find(text=re.compile('Page 1 of')).split(' ')[-1])

    @property
    def sections(self):
        return self.soup.select('.ResultsList_item')


class BioMedArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        self.title_tag = self.sec.select_one('.ResultsList_title > a')
        self.domain = 'http://{}.biomedcentral.com'\
            .format(JournalObj.site_source[:-1].split('/')[-1])
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title = self.title_tag.text.strip()

    @EP_METHOD
    def generate_authors(self):
        print(self.sec.select_one('.ResultsList_authors').text)
        self.authors = re.split(', | and ',self.sec.select_one('.ResultsList_authors').text.strip('…'))

    @EP_METHOD
    def generate_year(self):
        self.year = int(self.sec.select_one('.ResultsList_published').text.strip().split(' ')[-1])

    @EP_METHOD
    def generate_pdf_url(self):
        self.pdf_url = self.domain + self.sec.find("a",text=re.compile("PDF"))['href']

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = self.link.split('/')[-1]

    @EP_METHOD
    def generate_abstract(self):
        self.abstract = self.sec.select_one('.article_abstract').text.strip().strip('"')

    @EP_METHOD
    def generate_link(self):
        self.link = self.domain + self.title_tag['href']

if __name__=="__main__":
    parser = BioMedParser(from_web=False)
    print(parser.pages_amount)
    secs = parser.sections
    from Journals_Task.JournalClass import Journal
    j = Journal()
    j.site_source = 'http://www.biomedcentral.com/bmcbioinformatics/'
    for sec in secs:
        article = BioMedArticle(sec,j,2)
        article.show_in_cmd()