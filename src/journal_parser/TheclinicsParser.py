#coding:utf-8
"""
@file: theclinicsParser
@author: yaotong
@contact: Super.tyao@gmail.com
@python: 3.5
@editor: pycharm
@create: 2016-11-9 21:48
@description:
    Parser for theclinics
"""
import re
from bs4 import BeautifulSoup
from JournalArticle import JournalArticle
from decorators import except_pass
EP_METHOD = lambda func:except_pass(func,ModelName='TheclinicsArticle')

class TheclinicsParser:
    '''
        sample_url: http://www.emed.theclinics.com/issue/S0733-8627(16)X0004-1
    '''
    def __init__(self,html_source=None):
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def sections(self):
        return self.soup.select('.article-details')

class TheclinicsArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id,domain_index):
        self.domain = 'http://www.{}.theclinics.com'\
            .format(domain_index)#domain index可以由上层模块解析sample url得到
        self.sec = sec
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
       self.title = self.sec.select_one('.title').select_one('a').text

    @EP_METHOD
    def generate_authors(self):
       #self.authors = [ author.text for author in self.sec.select('.authors') ].split(',')
        self.authors = self.sec.select_one('.authors').text.split(', ')

    @EP_METHOD
    def generate_link(self):
        self.link = self.domain + '/article' + self.sec.select_one('.title').select_one('a')['href']

    @EP_METHOD
    def generate_year(self):
        self.year = int(self.sec.select_one('.published-online').text.strip().split(' ')[-1])

    @EP_METHOD
    def generate_pdf_url(self):
        self.pdf_url = self.domain + self.sec.find("a",text=re.compile("PDF"))['href']

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = self.sec.select_one('.doi').text.strip('DOI:').split('/')[-1]

if __name__=="__main__":
    '''
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.get('http://www.emed.theclinics.com/issue/S0733-8627(16)X0004-1')
    html = driver.page_source
    driver.close()
    '''
    with open('./pages/theclinic.html','rb') as f:
        html = f.read()
    from JournalClass import Journal
    journal = Journal()
    for sec in TheclinicsParser(html_source=html).sections:
        article = TheclinicsArticle(sec,journal,2,'emed')
        article.show_in_cmd()










































