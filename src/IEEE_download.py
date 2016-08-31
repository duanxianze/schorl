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
import os,psycopg2
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from IEEE_Parser import IEEE_HTML_Parser,Article

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
    def __init__(self,title):
        url = 'http://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=' + '%20'.join(title.split(' '))
        resp = requests.get(
            url = 'http://ieeexplore.ieee.org/rest/search',
            headers = {
                xxx
            }
        )
        print(resp.text)
        ihp = IEEE_HTML_Parser(
            soup = BeautifulSoup(resp.text,'lxml')
        )
        print(ihp.sections)
        self.sec = ihp.sections[0]

    def get_pdf_url(self):
        return Article(self.sec).pdf_url


class IEEE_PdfDownloader:
    def __init__(self,save_folder):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        self.save_folder = save_folder
        self.download_folder_files = os.listdir(save_folder)


    def get_unfinished_items(self,limit=10000):
        #从db中检索出出版社为IEEE的article title集
        cur.execute(
            "select title,google_id from articles where resource_link is null and journal_temp_info like '%ieee%' limit {}".format(limit)
        )
        return cur.fetchall()

    def download(self,unfinished_item):
        google_id = unfinished_item[1]
        pdf_url = IEEE_Search_Model(title=unfinished_item[0]).get_pdf_url()
        print(pdf_url)
        '''
        resp = requests.get(verify=False,url=ism.pdf_url())
        save_name = google_id + '.pdf'
        with open(
            os.path.join(self.save_folder, save_name), 'wb'
        ) as pdf_file:
            pdf_file.write(resp.content)
            self.download_folder_files.append(save_name)
        '''

    def run(self,thread_counts=16):
        print(self.get_unfinished_items(limit=100))
        '''
        pool = ThreadPool(thread_counts)
        pool.map(self.download,self.get_unfinished_items(100))
        pool.close()
        pool.join()
        '''

if __name__=='__main__':
    ipd = IEEE_PdfDownloader('ieee_download')
    ipd.download(
        unfinished_item = ['Multilayer suspended stripline and coplanar line filters','123123']
    )