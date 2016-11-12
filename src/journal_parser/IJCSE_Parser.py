#coding:utf-8
"""
@file:      IJCSE_Parser
@author:    yjh
@contact:
@python:    3.3
@editor:    PyCharm
@create:    2016-11-11 20:02
@description:
            Parser for IJCSE Publisher
"""
import re
from bs4 import BeautifulSoup
from JournalArticle import JournalArticle
from decorators import except_pass
EP_METHOD = lambda func:except_pass(func,ModelName='IJCSEArticle')

class IJCSEParser:
    '''
        sample_url: http://www.inderscience.com/info/inarticletoc.php?jcode=ijcse&year=2015&vol=10&issue=1/2

    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('./pages/IJCSE.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source, "html.parser")

    @property
    def sections(self):
        #return self.soup.find(valign = 'top').find_all( 'td', colspan="2")
        return self.soup.find_all('tr',valign='top')

class IJCSEArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        self.domain = 'http://www.inderscience.com/'
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title =  self.sec.find('a',href=re.compile('artid')).text.strip()

    @EP_METHOD
    def generate_authors(self):
        #self.authors = self.sec.find('br').get_text().split('DOI')[0]
        self.generate_title()
        self.authors = self.sec.find('td',colspan='2')\
            .text.strip(self.title).split('DOI')[0].split('; ')

    @EP_METHOD
    def generate_id_by_journal(self):
        self.generate_link()
        self.id_by_journal = self.link.strip(self.domain+'dx.doi.org')

    @EP_METHOD
    def generate_year(self):
        self.generate_id_by_journal()
        self.year = int(self.id_by_journal.split('.')[-2])

    @EP_METHOD
    def generate_link(self):
    	self.link =  self.sec.find("a",
             href=re.compile("http://dx.doi.org/"))['href']

    @EP_METHOD
    def generate_pdf_url(self):
        self.pdf_url =  self.sec.find("a",href=re.compile('aid'))['href']


if __name__=="__main__":
    from JournalClass import Journal
    journal = Journal()
    for sec in IJCSEParser(from_web=False).sections:
        article = IJCSEArticle(sec,journal,2)
        article.show_in_cmd()