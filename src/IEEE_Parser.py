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
    def __init__(self,soup=None,from_web=True):
        if soup:
            self.soup = soup
        if not from_web:
            print("from local file")
            with open('./IEEE Xplore Search Results.html', 'rb') as f:
                self.soup = BeautifulSoup(f.read(),'lxml')

    @property
    def sections(self):
        return self.soup.select('.List-results-items')


class Article:
    def __init__(self,sec):
        self.sec = sec
        self.List_items = sec.select('.List-item')

    @property
    #@except_or_none
    def title(self):
        pass

    @property
    @except_or_none
    def abstract(self):
        pass

    @property
    def pdf_page_url(self):
        for list_item in self.List_items:
            if list_item['ng-if'] == '::record.pdfLink':
                return list_item.select('a')[0]['href']
        return None

    @property
    @except_or_none
    def pdf_url(self):
        for i in range(1,10):
            print('try {} times...'.format(i))
            with requests.Session() as s:
                try:
                    soup = BeautifulSoup(
                        s.get(
                            url = self.pdf_page_url,
                            timeout=30,
                        ).text,"lxml"
                    )
                    return soup.find_all('frame')[1].get('src')
                except Exception as e:
                    print('pdf_url() Error:{}'.format(str(e)))
        raise Exception('Cannot get it in 10 times')

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
    for sec in IEEE_HTML_Parser(from_web=False).sections:
        Article(sec).show_in_cmd()