#coding:utf-8
"""
@file:      IEEE_Parser.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-31 17:16
@description:
            --
"""

import requests,random
from bs4 import BeautifulSoup
from ua_pool import agents



def except_or_none(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print('IEEE_Article_Parser:\n\tError in {}(): {}'.format(func.__name__,str(e)))
            return None
    return wrapper


class IEEE_HTML_Parser:
    def __init__(self,driver):
        self.driver = driver

    @property
    def sections(self):
        return self.driver.find_elements_by_class_name('List-results-items')


class Article:
    def __init__(self,sec):
        self.sec = sec
        self.List_items = sec.find_elements_by_class_name('List-item')

    @property
    @except_or_none
    def title(self):
        pass

    @property
    @except_or_none
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
        for i in range(1,10):
            #print('IEEE_Article_Parser:\n\ttry {} times to get pdf_url in frame...'.format(i))
            with requests.Session() as s:
                try:
                    soup = BeautifulSoup(
                        s.get(
                            url = self.pdf_page_url,
                            timeout=30,
                            headers = {
                                'User-Agent':random.choice(agents)
                            }
                        ).text,"lxml"
                    )
                    return soup.find_all('frame')[1].get('src')
                except Exception as e:
                    pass
                    #print('IEEE_Article_Parser:\n\tpdf_url() Error:{}'.format(str(e)))
        print('IEEE_Article_Parser:\n\tCannot get it in 10 times')
        return None

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