#coding:utf-8
"""
@file:      Spring_Parser.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 19:55
@description:
            ??
"""
from bs4 import BeautifulSoup
from src.crawl_tools.request_with_proxy import request_with_random_ua

class SpringParser:
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('Spring.html','rb') as f:
                html_source = f.read()
        self.soup = BeautifulSoup(html_source,'lxml')

    @property
    def pages_amount(self):
        return int(self.soup.select_one('.number-of-pages').text)

    @property
    def secs(self):
        return self.soup.select_one('#results-list').select('li')


class SpringArticle:
    def __init__(self,sec):
        self.sec = sec

    @property
    def title(self):
        return self.sec.select_one('.title').text

    @property
    def authors(self):
        return list(map(lambda x:x.text,self.sec.select_one('.authors').select('a')))

    @property
    def link(self):
        return 'http://link.springer.com' + self.sec.select_one('.title')['href']

    @property
    def abstract(self):
        return self.sec.select_one('.snippet').text

    @property
    def year(self):
        return int(self.sec.select_one('.year').text[1:-1])

    @property
    def pdf_url(self):
        try:
            return 'http://link.springer.com'+self.sec.select_one('.pdf-link')['href']
        except:
            return None

    @property
    def id_by_journal(self):
        return

    def show_in_cmd(self):
        print('title:{}'.format(self.title))
        print('authors:{}'.format(self.authors))
        print('link:{}'.format(self.link))
        print('abstract:{}'.format(self.abstract))
        print('pdf_url:{}'.format(self.pdf_url))
        print('year:{}'.format(self.year))
        print('id_by_journal:{}'.format(self.id_by_journal))



if __name__=="__main__":
    for sec in SpringParser(from_web=False).secs:
        SpringArticle(sec).show_in_cmd()
        print('------------')


