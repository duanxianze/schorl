#coding:utf-8
"""
@file:      PdfUrlGenerator.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-06 19:18
@description:
            The basic class of pdf url generator for different journals
"""

from multiprocessing.dummy import Pool as ThreadPool
from src.crawl_tools import DriversPool
import os,psycopg2

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


class PdfUrlGenerator:
    def __init__(self):
        self.drivers_pool = []

    def _get_unfinished_items(self,query_sql):
        cur.execute(query_sql)
        return cur.fetchall()

    def _generate(self,unfinished_item,google_id_index,get_pdf_url_func):
        google_id = unfinished_item[google_id_index]
        print('{}_PDF_URL_Generator:\n\tGot task of {}'.format(self.__class__,google_id))
        driverObj = self.drivers_pool.get_one_free_driver(wait=True)
        driverObj.status = 'busy'
        pdf_url = get_pdf_url_func(driver=driverObj.engine,unfinished_item=unfinished_item)
        driverObj.status = 'free'
        if pdf_url:
            print('{}_PDF_URL_Generator:\n\tGot pdf_url of {}:{}'.format(self.__class__,google_id,pdf_url))
            self.mark_db(pdf_url,google_id)
        else:
            print('{}_PDF_URL_Generator:\n\tFail to get pdf_url of {}'.format(self.__class__,google_id))

    def mark_db(self,pdf_url,google_id):
        try:
            sql = "update articles set resource_link = '{}',resource_type = 'PDF' where google_id = '{}'".format(pdf_url,google_id)
            cur.execute(sql)
            print('Database:\n\tUpdate pdf_url of {} ok '.format(google_id))
        except Exception as e:
            print('Except sql is:\n\t{}'.format(sql))
            print('Database:\n\tMark Error:{}'.format(str(e)))

    def run(self,thread_counts=16,visual=True,limit=1000):
        task_pool = ThreadPool(thread_counts)
        print(type(task_pool))
        self.drivers_pool = DriversPool(
            size = thread_counts,
            visual = visual,
            launch_with_thread_pool = task_pool
        )
        while(1):
            result = task_pool.map(self.generate,self.get_unfinished_items(limit))
            print(result)
            task_pool.close()
            task_pool.join()