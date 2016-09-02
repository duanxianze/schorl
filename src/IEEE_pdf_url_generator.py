#coding:utf-8
"""
@file:      IEEE_download.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-08-31 14:43
@description:
            专门为IEEE出版社的pdf下载模块
"""

import requests
import os,psycopg2,random
from multiprocessing.dummy import Pool as ThreadPool
from IEEE_Parser import IEEE_HTML_Parser,Article,get_pdf_link
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


class IEEE_Search_Model:
    def __init__(self,title,viusal=False):
        self.title = title
        if viusal:
            driver = webdriver.Chrome()
        else:
            driver = webdriver.PhantomJS()
        while(1):
            driver.get(
                url = 'http://ieeexplore.ieee.org/search/searchresult.jsp?queryText={}&newsearch=true'\
                    .format('%20'.join(title.split(' ')))
            )#尝试selenium进入搜索页
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'List-results-items'))
                )#等待网站的ajax加载完，items呈现在页面上，交给parser处理
                try:
                    title = title[:40]
                except:
                    pass
                print('IEEE_Search_Model:\n\tGot search result of <{}>\n\tDeliver to parser...'.format(title+'...'))
                break
            except Exception as e:
                print('IEEE_Search_Model:\n\tError in search page:{}, reload again...'.format(str(e)))
        self.sec = IEEE_HTML_Parser(driver).sections[0]

    def get_pdf_url(self):
        pdf_page_url = Article(self.sec).pdf_page_url
        if pdf_page_url:
            cur.execute(
                "update articles set pdf_temp_url = '{}' where title = '{}'".format(pdf_page_url,self.title)
            )
            return get_pdf_link(pdf_page_url)


class IEEE_pdf_url_generator:
    def __init__(self):
        pass

    def get_unfinished_items(self,limit=10000):
        #从db中检索出出版社为IEEE的article title集
        cur.execute(
            "select title,google_id from articles where resource_link is null and journal_temp_info like '%ieee%' limit {}".format(limit)
        )
        return cur.fetchall()

    def get_pdf_temp_url_in_db(self,google_id):
        cur.execute(
            "select pdf_temp_url from articles where google_id = %s",
            (google_id,)
        )
        data = cur.fetchall()
        print(data)
        if data:
            return data[0][0]
        else:
            return None

    def generate(self,unfinished_item):
        google_id = unfinished_item[1]
        print('IEEE_PDF_URL_Generator:\n\tGot task of {}\n'.format(google_id))
        pdf_temp_url = self.get_pdf_temp_url_in_db(google_id)
        #print('pdf_temp_url:{}'.format(pdf_temp_url))
        if pdf_temp_url:
            pdf_url = get_pdf_link(pdf_temp_url)
        else:
            pdf_url = IEEE_Search_Model(
                title = unfinished_item[0]
            ).get_pdf_url()
        if not pdf_url:
            print('IEEE_PDF_URL_Generator:\n\tFail to get pdf_url of {}'.format(google_id))
            return
        print('IEEE_Article_Parser:\n\tGot pdf_url:{}'.format(pdf_url))
        self.mark_db(pdf_url,google_id)

    def mark_db(self,pdf_url,google_id):
        cur.execute(
            "update articles set resource_link = %s,resource_type = 'PDF' where google_id = %s",
            (pdf_url,google_id)
        )
        print('Database:\n\tupdate pdf_url of {} ok '.format(google_id))

    def run(self,thread_counts=16):
        pool = ThreadPool(thread_counts)
        pool.map(self.generate,self.get_unfinished_items(100))
        pool.close()
        pool.join()


if __name__=='__main__':
    ipd = IEEE_pdf_url_generator()
    '''
    ipd.download(
        unfinished_item = ['Multilayer suspended stripline and coplanar line filters','123123']
    )
    '''
    ipd.run(thread_counts=4)