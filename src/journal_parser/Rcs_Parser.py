# -*- coding: utf-8 -*-
"""
@file:      Rcs_Parser
@author:    WYn
@contact:   genius_wz@aliyun.com
@python:    2.7.10
@editor:    pyCharm
@create:    2016-11-11 19:37
@description:
            Parser for Rcs publish
"""
import re
from bs4 import BeautifulSoup
from JournalArticle import JournalArticle
from decorators import except_pass
EP_METHOD = lambda func:except_pass(func,ModelName='RcsArticle')

class RcsParser:
    '''
        http://pubs.rsc.org/en/journals/journalissues/lc#!issueid=lc016022&type=current&issnprint=1473-0197
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('./pages/Rcs.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'html.parser')

    @property
    def sections(self):
        return self.soup.find_all(class_='grey_box_wrapper')


class RcsArticle(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id):
        self.sec = sec
        self.domain = 'http://pubs.rsc.org'
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title=self.sec.find(class_='grey_box_right_s4_jrnls').find('a').text.strip()

    @EP_METHOD
    def generate_authors(self):
        #self.authors = [author for author in self.sec.find(class_='red_txt_s4').text.strip().split(',')]
        authors_text = self.sec.find(class_='red_txt_s4').text.strip()
        self.authors = re.split(', | and ',authors_text)

    @EP_METHOD
    def generate_year(self):
        self.year = int(self.sec.find(class_='grey_left_box_text_s4_new').get_text().strip().split(',')[1])

    @EP_METHOD
    def generate_pdf_temp_url(self):
        self.pdf_temp_url = self.domain + self.sec.find(class_='pdf_link_s4_jrnls').find('a')['href']

    @EP_METHOD
    def generate_id_by_journal(self):
        #self.id_by_journal = self.sec.find(class_='grey_left_box_text_s4_new').find('br').text.strip()
        self.id_by_journal = self.sec.find(class_='grey_left_box_text_s4_new')\
            .text.strip().split('DOI: ')[-1].split(' ')[0]

    @EP_METHOD
    def generate_abstract(self):
        self.abstract = self.sec.find('div',attrs={'title':'Brief Abstract'}).text.strip()

    @EP_METHOD
    def generate_link(self):
        self.link = self.domain + self.sec.find('a',attrs={'href':re.compile('/en/content/articlelanding')})['href']

if __name__=="__main__":
    from JournalClass import Journal
    journal = Journal()

    for sec in RcsParser(from_web=False).sections:
        article = RcsArticle(sec,journal,3)
        article.show_in_cmd()