#coding:utf-8
"""
@file:      IEEE_Parser.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-31 17:16
@description:
            解析IEEE搜索结果页
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

import requests,random,re
from bs4 import BeautifulSoup
from selenium import webdriver
from crawl_tools.ua_pool import get_one_random_ua
from crawl_tools.request_with_proxy import request_with_proxy
from journal_parser.JournalArticle import JournalArticle
from crawl_tools.decorators import except_pass,except_return_none
ERN_METHOD = lambda func:except_return_none(func,'IEEE_PARSER')
EP_METHOD = lambda func:except_pass(func,'IEEE_ARTICLE')

'''
@except_or_none
def get_pdf_link(pdf_page_url):
    with requests.Session() as s:
        soup = BeautifulSoup(
            s.get(
                url = pdf_page_url,
                timeout=30,
                headers = {
                    'User-Agent':get_one_random_ua()
                }
            ).text,"lxml"
        )
        try:
            soup.find_all('frame')[1].get('src')
        except:
            print(soup)
'''

def get_ieee_pdf_link(pdf_page_url,driver):
    driver.get(pdf_page_url)
    soup = BeautifulSoup(driver.page_source,'lxml')
    try:
        return soup.find_all('frame')[1].get('src')
    except Exception as e:
        print('[Error] in IEEE_Parser:get_ieee_pdf_link():{}'.format(str(e)))
        print('The url of issue is {}'.format(pdf_page_url))
        return None


class IEEE_HTML_Parser:
    '''
        the sample url is: http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=hello&newsearch=true
    '''
    def __init__(self,driver):
        self.driver = driver

    @property
    @ERN_METHOD
    def sections(self):
        return self.driver.find_elements_by_class_name('List-results-items')


class Article:
    def __init__(self,sec,driver=None):
        self.driver = driver
        self.sec = sec
        self.List_items = sec.find_elements_by_class_name('List-item')

    @property
    def title(self):
        pass

    @property
    def abstract(self):
        pass

    @property
    def pdf_page_url(self):
        for list_item in self.List_items:
            if list_item.get_attribute('ng-if')=='::record.pdfLink':
                return list_item.find_element_by_tag_name('a').get_attribute('href')
        return None

    @property
    def pdf_url(self):
        return get_ieee_pdf_link(self.pdf_page_url,self.driver)

    @property
    @ERN_METHOD
    def html_url(self):
        pass

    @property
    @ERN_METHOD
    def authors(self):
        pass

    def show_in_cmd(self):
        print('**************New Article Info******************')
        print('title:\t\t{}'.format(self.title))
        print('abstract:\t{}'.format(self.abstract))
        print('pdf_page_url:\t\t{}'.format(self.pdf_page_url))
        print('pdf_url:\t\t{}'.format(self.pdf_url))
        print('html_url:\t{}'.format(self.html_url))
        print('authors:\t{}'.format(self.authors))
        print('**************New Article Info******************')


class IEEE_AllItemsPageParser:
    '''
        For all-article page of specific journal by year.
        The sample url is http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=5480&punumber=83
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('IEEE_Journal.html','r') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def volume_links(self):
        return list(map(
            lambda x:'http://ieeexplore.ieee.org'+x['href'],
            self.soup.select_one('.volumes').select('a')))

    @property
    def volume_year(self):
        year_string = self.soup.select_one('.heading')\
            .select_one('h2').text.strip().split(' ')[-1]
        try:
            return int(year_string)
        except:
            return int(year_string[-4:])

    @property
    def sections(self):
        return self.soup.select_one('.results').select('li')

class IEEE_Article(JournalArticle):
    def __init__(self,sec,JournalObj,volume_db_id,year):
        self.sec = sec
        self.title_text_span = self.sec.find(
            id = re.compile("art-abs-title-[0-9]+")
        )
        if not self.title_text_span:
            raise Exception('IEEE article type Error')
        JournalArticle.__init__(self,JournalObj,volume_db_id)
        self.year = year
        self.title_parent_a_tag = self.title_text_span.parent
        self.generate_all_method()

    @EP_METHOD
    def generate_title(self):
        self.title = self.title_text_span.text

    @EP_METHOD
    def generate_authors(self):
        self.authors = list(map(
            lambda x:x['data-author-name'],
            self.sec.select('#preferredName')
        ))

    @EP_METHOD
    def generate_link(self):
        self.link = 'http://ieeexplore.ieee.org'+self.title_parent_a_tag['href']

    @EP_METHOD
    def generate_abstract(self):
        self.abstract = self.sec.select_one('.abstract').text.strip()

    @EP_METHOD
    def generate_pdf_temp_url(self):
        self.pdf_temp_url = 'http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+self.title_parent_a_tag['data-arnumber']

    @EP_METHOD
    def generate_id_by_journal(self):
        self.id_by_journal = 'IEEE'+self.title_parent_a_tag['data-arnumber']


if __name__=="__main__":
    from Journals_Task.JournalClass import Journal
    parser = IEEE_AllItemsPageParser(from_web=False)
    JournalObj=Journal()
    JournalObj.site_source = 'http://www.elsevier.com/wps/find/journaldescription.cws_home/505606/description#description'
    JournalObj.sjr_id = 123
    print(parser.volume_links)
    for link in parser.volume_links:
        print(link)
    '''
    for sec in parser.sections:
        IEEE_Article(sec,JournalObj,year=parser.volume_year).show_in_cmd()
    '''