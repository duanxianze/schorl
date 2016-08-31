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

import os,psycopg2,requests,random
from bs4 import BeautifulSoup
from ua_pool import agents

if os.name is 'nt':
    conn = psycopg2.connect(
        host = '45.32.131.53',
        port = 5432,
        dbname = "sf_development",
        user = "gao",
        password = "gaotongfei13"
    )
else:
    conn = psycopg2.connect(
        dbname = "sf_development",
        user = "gao",
        password = "gaotongfei13"
    )
cur = conn.cursor()
conn.autocommit = True

def except_or_none(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print('IEEE_Article_Parser:\n\tError in {}(): {}'.format(func.__name__,str(e)))
            return None
    return wrapper


class IEEE_HTML_Parser:
    def __init__(self,soup):
        self.soup = soup

    @property
    def sections(self):
        return self.soup.select('.List-results-items')


class Article:
    def __init__(self,sec):
        self.sec = sec
        self.List_items = sec.select('.List-item')

    @property
    @except_or_none
    def title(self):
        pass

    @property
    @except_or_none
    def abstract(self):
        pass

    @property
    @except_or_none
    def pdf_page_url(self):
        for list_item in self.List_items:
            if list_item.get_attribute('ng-if') is '::record.pdfLink':
                return list_item.find_element_by_tag_name('a').get_attribute('href')
            else:
                print(list_item.get_attribute('ng-if'))
        return None

    @property
    @except_or_none
    def pdf_url(self):
        session = requests.Session()
        with session as s:
            print(self.pdf_page_url)
            r = s.get(
                url = self.pdf_page_url,
                timeout=10,
                headers = {'User-Agent':random.choice(agents)}
            )
            #time.sleep(30)
            print(r.status_code)
            if r.status_code==200:
                soup = BeautifulSoup(r.text, "lxml")
                return soup.find_all('frame')[1].get('src')
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
        print('pdf_url:\t\t{}'.format(self.pdf_url))
        print('html_url:\t{}'.format(self.html_url))
        print('authors:\t{}'.format(self.authors))
        print('**************New Article Info******************')



if __name__=="__main__":
    for sec in IEEE_HTML_Parser(
        url='http://ieeexplore.ieee.org/search/searchresult.jsp?queryText=Multilayer&newsearch=true'
    ).sections:
        Article(sec).show_in_cmd()