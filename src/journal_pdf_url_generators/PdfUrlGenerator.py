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
from src.crawl_tools.DriversPool import DriversPool
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
    def __init__(self,query_sql):
        self._drivers_pool = []
        self._task_thread_pool = []
        self.query_sql = query_sql
        print(self.query_sql)

    def _get_unfinished_items(self):
        cur.execute(self.query_sql)
        return cur.fetchall()

    def _generate(self,unfinished_item,google_id_index,get_pdf_url_func):
        google_id = unfinished_item[google_id_index]
        print('PDF_URL_Generator:\n\tGot task of {}'.format(google_id))
        driverObj = self._drivers_pool.get_one_free_driver(wait=True)
        driverObj.status = 'busy'
        pdf_url = get_pdf_url_func(driver=driverObj.engine,unfinished_item=unfinished_item)
        driverObj.status = 'free'
        if pdf_url:
            print('PDF_URL_Generator:\n\tGot pdf_url of {}:{}'.format(google_id,pdf_url))
            self._mark_db(pdf_url,google_id)
        else:
            print('PDF_URL_Generator:\n\tFail to get pdf_url of {}'.format(google_id))

    def _mark_db(self,pdf_url,google_id):
        try:
            sql = "update articles set resource_link = '{}',resource_type = 'PDF' where google_id = '{}'".format(pdf_url,google_id)
            cur.execute(sql)
            print('Database:\n\tUpdate pdf_url of {} ok '.format(google_id))
        except Exception as e:
            print('Except sql is:\n\t{}'.format(sql))
            print('Database:\n\tMark Error:{}'.format(str(e)))

    def _run(self,thread_counts=16,visual=True):
        self._task_thread_pool = ThreadPool(thread_counts)
        self._drivers_pool = DriversPool(
            size = thread_counts,
            visual = visual,
            launch_with_thread_pool = self._task_thread_pool
        )