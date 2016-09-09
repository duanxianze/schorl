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
from crawl_tools.SQL_Generator import SQL_Generator,SQL_Parser
from db_config import cur
import random

class PdfUrlGenerator:
    def __init__(self):
        self._drivers_pool = []
        self._task_thread_pool = []

    def _get_max_unfinished_item_id(self,max_id_where_sqls):
        origin_sql = 'SELECT max(id) FROM articles'
        paras_dict = SQL_Parser(origin_sql).to_dict()
        if 'WHERE' not in paras_dict.keys():
            paras_dict['WHERE'] = []
        for max_id_where_sql in max_id_where_sqls:
            paras_dict['WHERE'].append(max_id_where_sql)
        sql = SQL_Generator(paras_dict).to_sql()
        #print(sql)
        cur.execute(sql)
        return cur.fetchall()[0][0]

    def _get_unfinished_items(self,query_sql,max_id_where_sqls,
            add_where_sqls=[],left=0,length=1000):
        '''
        where_sql_list is like: [
            ['resource_link', 'is', 'null'],
            ['id', '>', 200]
        ]
        '''
        max_id = self._get_max_unfinished_item_id(max_id_where_sqls)
        print('PdfUrlGenerator:\n\tMax_id = {}'.format(max_id))
        try:
            left = random.randint(1,max_id-length)
        except:
            left = 0
        right = left + length
        add_where_sqls.append(['id','>',left])
        add_where_sqls.append(['id','<',right])
        paras_dict = SQL_Parser(query_sql).to_dict()
        for where_sql in add_where_sqls:
            paras_dict['WHERE'].append(where_sql)
        query_sql = SQL_Generator(paras_dict).to_sql()
        cur.execute(query_sql)
        data = cur.fetchall()
        print("PdfUrlGenerator:\n\tLoading {} items in range[{},{}]".format(len(data),left,right))
        return data

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
            sql = "update articles set resource_link = '{}',resource_type = 'PDF' \
                    where google_id = '{}'".format(pdf_url,google_id)
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