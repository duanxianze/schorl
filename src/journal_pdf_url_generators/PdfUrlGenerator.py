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
from crawl_tools.DriversPool import DriversPool
from crawl_tools.Timer import Timer
from db_config import cur

class PdfUrlGenerator:
    def __init__(self):
        self._drivers_pool = []
        self._task_thread_pool = []

    def _get_unfinished_items(self,query_sql):
        cur.execute(query_sql)
        return cur.fetchall()

    def _generate(self,unfinished_item,google_id_index,get_pdf_url_func):
        google_id = unfinished_item[google_id_index]
        print('PDF_URL_Generator:\n\tGot task of {}'.format(google_id))
        tik = Timer()
        tik.start()
        driverObj = self._drivers_pool.get_one_free_driver(wait=True)
        driverObj.status = 'busy'
        pdf_url = None
        try:
            pdf_url = get_pdf_url_func(
                unfinished_item = unfinished_item,
                driver = driverObj.engine
            )#本函数由子类的generator自行判断书写
        except Exception as e:
            print('[Error] in PdfUrlGenerator__get_pdf_url():\n\t{}'.format(str(e)))
        driverObj.status = 'free'
        if pdf_url:
            self._mark_db(pdf_url,google_id)
            tik.end()
            print('PDF_URL_Generator:\n\tFinish task in {} s\
                    \n\tGot pdf_url of {}:{}'.format(tik.gap,google_id,pdf_url))
        else:
            print('PDF_URL_Generator:\n\tFail to get pdf_url of {}'.format(google_id))

    def _mark_db(self,pdf_url,google_id):
        try:
            sql = "update articles set resource_link = '{}',resource_type = 'PDF' where google_id = '{}'".format(pdf_url,google_id)
            cur.execute(sql)
            print('Database:\n\tUpdate pdf_url of {} ok '.format(google_id))
        except Exception as e:
            print('Except SQL is:\n\t{}'.format(sql))
            print('Database:\n\tMark Error:{}'.format(str(e)))

    def _run(self,thread_counts=16,visual=True):
        self._task_thread_pool = ThreadPool(thread_counts)
        self._drivers_pool = DriversPool(
            size = thread_counts,
            visual = visual,
            launch_with_thread_pool = self._task_thread_pool
        )

    def _close(self):
        self._task_thread_pool.close()
        self._task_thread_pool.join()
        self._drivers_pool.close()