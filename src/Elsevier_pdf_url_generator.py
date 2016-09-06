#coding:utf-8
"""
@file:      Elsevier_pdf_url_generator.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-06 13:18
@description:
            从db中获得elsevier杂志社的文章title集合，
            生成pdf_url反馈给db
"""
import os,psycopg2
from Elsevier_Parser import Elsevier_Parser
from multiprocessing.dummy import Pool as ThreadPool

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


class Elsevier_pdf_url_generator:
    def __init__(self):
        pass

    def get_unfinished_items(self,limit=10000):
        #从db中检索出出版社为Elsevier的article title集
        cur.execute(
            "select link,google_id from articles where resource_link is null and journal_temp_info like '%Elsevier%' limit {}".format(limit)
        )
        return cur.fetchall()

    def generate(self,unfinished_item):
        google_id = unfinished_item[1]
        print('Elsevier_PDF_URL_Generator:\n\tGot task of {}'.format(google_id))
        pdf_url = Elsevier_Parser(
            article_page_url=unfinished_item[0]
        ).pdf_url
        if not pdf_url:
            print('Elsevier_PDF_URL_Generator:\n\tFail to get pdf_url of {}'.format(google_id))
            return
        else:
            print('Elsevier_PDF_URL_Generator:\n\tGot pdf_url of {}:{}'.format(google_id,pdf_url))
        self.mark_db(pdf_url,google_id)

    def mark_db(self,pdf_url,google_id):
        try:
            sql = "update articles set resource_link = '{}',resource_type = 'PDF' where google_id = '{}'".format(pdf_url,google_id)
            cur.execute(sql)
            print('Database:\n\tupdate pdf_url of {} ok '.format(google_id))
        except Exception as e:
            print('Except sql is:\n\t{}'.format(sql))
            print('Database:\n\tMark Error:{}'.format(str(e)))

    def run(self,thread_counts=16):
        task_pool = ThreadPool(thread_counts)
        while(1):
            result = task_pool.map(self.generate,self.get_unfinished_items(1000))
            print(result)
            task_pool.close()
            task_pool.join()

if __name__=='__main__':
    Elsevier_pdf_url_generator().run(thread_counts=32)
