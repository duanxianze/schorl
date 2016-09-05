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

import requests,random
from bs4 import BeautifulSoup
from selenium import webdriver
from ua_pool import agents
from request_with_proxy import request_with_proxy


def except_or_none(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print('IEEE_Article_Parser:\n\tError in {}(): {}'\
                  .format(func.__name__,str(e)))
            return None
    return wrapper

'''
@except_or_none
def get_pdf_link(pdf_page_url):
    with requests.Session() as s:
        soup = BeautifulSoup(
            s.get(
                url = pdf_page_url,
                timeout=30,
                headers = {
                    'User-Agent':random.choice(agents)
                }
            ).text,"lxml"
        )
        try:
            soup.find_all('frame')[1].get('src')
        except:
            print(soup)
'''

@except_or_none
def get_pdf_link(pdf_page_url,driver):
    driver.get(pdf_page_url)
    soup = BeautifulSoup(driver.page_source,'lxml')
    return soup.find_all('frame')[1].get('src')


class IEEE_HTML_Parser:
    def __init__(self,driver):
        self.driver = driver

    @property
    @except_or_none
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
        return get_pdf_link(self.pdf_page_url,self.driver)

    @property
    @except_or_none
    def html_url(self):
        pass

    @property
    @except_or_none
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


if __name__=="__main__":
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.get(url = 'http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=123&newsearch=true')
    for sec in IEEE_HTML_Parser(driver).sections:
        Article(sec).show_in_cmd()