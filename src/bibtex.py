#coding:utf-8
"""
@file:      bibtex.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-26 14:08
@description:
            获取articles的bibtex
"""

from bs4 import BeautifulSoup
from random import randint
from request_with_proxy import request_with_proxy
import psycopg2
import time,random

random_port = lambda x, y: randint(x, y)#随机分配端口

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
            print('Bibtex:\n\tError in {}(): {}'.format(func.__name__,str(e)))
            return None
    return wrapper

class Bibtex:
    def __init__(self,soup,article_id=None):
        self.soup = soup
        if article_id:
            self.article_id = article_id

    @property
    @except_or_none
    def citi(self):
        return self.soup.select("#gs_citi > a")

    @property
    @except_or_none
    def url(self):
        if self.citi:
            return self.citi[0]['href']

    @property
    @except_or_none
    def text(self):
        for i in range(1,10):
            print('Bibtex:\n\t{} times trying to get bibtex from {}...'.format(i,self.url))
            bibtex_response = request_with_proxy(self.url)
            print('bibtex site status code: {}'.format(bibtex_response.status_code))
            if bibtex_response:
                bibtex = bibtex_response.text
                print('Bibtex:\n\tGet new bibtex of the article:{}\n\t{}'.format(self.article_id,bibtex))
                return bibtex
            time.sleep(3)
        return None

    def save_to_db(self):
        if self.text:
            try:
                cur.execute(
                    "update articles set bibtex = %s where id = %s",
                    (self.text, self.article_id)
                )
            except Exception as e:
                print('Bibtex:Error:save_to_db():\n\t{}'.format(str(e)))


class BibtexSpider:
    def __init__(self):
        pass

    @property
    def unfinished_items(self):
        cur.execute(
            "select id, google_id from articles where id > 314083 and bibtex is null and google_id is not null"
        )
        return cur.fetchall()

    def run(self,shuffle=True):
        while(1):
            unfinished_items = self.unfinished_items
            random.shuffle(unfinished_items)
            for id, google_id in unfinished_items:
                url = 'https://scholar.google.com/scholar?q=info:{}:scholar.google.com/&output=cite&scirp=0&hl=en'.format(google_id)
                print("BibtexSpider:\n\tid: {0} google_id: {1} url:{2}".format(id, google_id,url))
                for i in range(1,10):
                    print('BibtexSpider:\n\t{} times to enter first page...')
                    response = request_with_proxy(url)
                    if response.status_code == 200:
                        print("response 200")
                        Bibtex(
                            soup = BeautifulSoup(response.text, "lxml"),
                            article_id = id
                        ).save_to_db()
                    else:
                        print(response.status_code)
                    time.sleep(3)


if __name__=='__main__':
    BibtexSpider().run()