#coding:utf-8
"""
@file:      got_journals_info.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-15 14:30
@description:
            ??
"""

from src.journal_parser.SJR_Parser import *
from src.crawl_tools.DriversPool import DriversPool
from multiprocessing.dummy import Pool as ThreadPool
from src.db_config import new_db_cursor
cur = new_db_cursor()


class JournalInfoGenerator:
    def __init__(self):
        drivers_cot = 8
        self.thread_pool = ThreadPool(drivers_cot)
        self.drivers_pool = DriversPool(
            visual=False,    size=drivers_cot,
            launch_with_thread_pool=self.thread_pool,
        )

    def get_db_category_ids(self):
        cur.execute(
            'select sjr_id,area_id from sjr_category'
        )
        return cur.fetchall()

    def get_rank_journal_info(self,db_item):
        driverObj = self.drivers_pool.get_one_free_driver()
        driverObj.status = 'busy'
        for sec in JournalRankPageParser(
            category_id = db_item[0],
            area_id = db_item[1],
            driver = driverObj.engine
        ).secs:
            journal = RankJournal(sec)
            journal.save_to_db(db_item[0])
            #print(sec.text)
            print('----------')
        driverObj.status = 'free'

    def get_db_journal_ids(self):
        cur.execute(
            'select sjr_id from journal'
        )

    def get_detail_journal_info(self,db_item):

    def run(self,mode):
        if mode==1:
            #mode 1 是在第一阶段,rank页journal没有全拿下来之前
            #主要是为了初始化生成条目
            self.thread_pool.map(
                self.get_rank_journal_info,
                self.get_db_category_ids()
            )
        elif mode==2:
            #mode 2 第二阶段，进入详情页拿信息
            #出发点是从阶段一中的条目开始
            pass
        else:
            pass


if __name__=="__main__":
    JournalInfoGenerator().run(mode=1)

