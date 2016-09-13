#coding:utf-8
"""
@file:      bibtex.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-26 14:08
@description:
            获取articles的bibtex(bs4版本)
"""
import os,sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from db_config import cur
from crawl_tools.request_with_proxy import request_with_proxy

from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
import time,random

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
            url = self.url
            print('Bibtex:\n\t{} times trying to get bibtex of article_id = {}\n\turl:{}'.format(i,self.article_id,url))
            bibtex_response = request_with_proxy(url)
            print('Bibtex:\n\tbibtex site status code: {}'.format(bibtex_response.status_code))
            if bibtex_response:
                bibtex = bibtex_response.text
                print('Bibtex:\n\t[SUCCESS] to get new bibtex of the article: {}\n{}'.format(self.article_id,bibtex))
                return bibtex
            time.sleep(random.randint(1,4))
        return None

    def save_to_db(self):
        if self.text:
            try:
                cur.execute(
                    "update articles set bibtex = %s where id = %s",
                    (self.text, self.article_id)
                )
                print('Bibtex:\n\tSave article: {} OK!'.format(self.article_id))
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

    def crawl(self,unfinished_item):
        id = unfinished_item[0]
        google_id = unfinished_item[1]
        url = 'https://scholar.google.com/scholar?q=info:{}:scholar.google.com/&output=cite&scirp=0&hl=en'.format(google_id)
        print("BibtexSpider:\n\tid: {0} google_id: {1} \n\turl:{2}".format(id, google_id,url))
        for i in range(1,10):
            print('BibtexSpider:\n\t{} times to enter article_id = {} first page...'.format(i,id))
            response = request_with_proxy(url)
            if response.status_code == 200:
                print("BibtexSpider:\n\tFirst page ok!Response 200...")
                Bibtex(
                    soup = BeautifulSoup(response.text, "lxml"),
                    article_id = id
                ).save_to_db()
                return
            else:
                print('BibtexSpider:\n\tFirst page visit error:Responese {}'.format(response.status_code))
            time.sleep(random.randint(1,4))

    def run(self,thread_counts=4,shuffle=True):
        pool = ThreadPool(thread_counts)
        unfinished_items = self.unfinished_items
        if shuffle:
            random.shuffle(unfinished_items)
        pool.map(self.crawl, unfinished_items)
        pool.close()
        pool.join()



if __name__=='__main__':
    BibtexSpider().run(thread_counts=16)
