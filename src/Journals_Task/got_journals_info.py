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


class JournalInfoGenerator:
    def __init__(self):
        pass

    def get_db_category_ids(self):
        cur = new_db_cursor()
        cur.execute(
            'select sjr_id,area_id from sjr_category ORDER by id desc'
        )
        return cur.fetchall()

    def is_crawled_in_rank_page(self,category_id):
        '''
            判断某领域第一阶段是否爬过
            搜索category和journal的关联表
            若结果数多于10则说明已爬（多了也不需要）
        '''
        cur = new_db_cursor()
        sql = 'select count(*) from journal_category where category_id = {}'.format(category_id)
        #print(sql)
        cur.execute(sql)
        amount = cur.fetchall()[0][0]
        print('JournalInfoGenerator:\n\tCategory_id:{},Amount:{}'.format(category_id,amount))
        cur.close()
        return amount>10

    def get_rank_journal_info(self,db_item):
        #print(db_item)
        category_id = db_item[0]
        print('JournalInfoGenerator:\n\tGot task of {}'.format(category_id))
        if self.is_crawled_in_rank_page(category_id):
            print('JournalInfoGenerator:\n\t[Category crawled] {}'\
                  .format(category_id))
            return
        driverObj = self.drivers_pool.get_one_free_driver()
        driverObj.status = 'busy'
        try:
            for sec in JournalRankPageParser(
                category_id = db_item[0],
                area_id = db_item[1],
                driver = driverObj.engine
            ).secs:
                RankJournal(sec).save_to_db(db_item[0])
        except Exception as e:
            print('JournalInfoGenerator:\n\t[Error] in get_rank_journal_info:{}'.format(str(e)))
        driverObj.status = 'free'

    def get_db_journal_ids(self):
        cur = new_db_cursor()
        cur.execute(
            #'select sjr_id from journal WHERE is_crawled=FALSE '
            'select sjr_id from journal'
        )
        journal_ids = cur.fetchall()
        cur.close()
        return journal_ids

    def get_detail_journal_info(self,db_item):
        JournalDetailPageParser(journal_sjr_id=db_item[0])\
            .save_journal_area()

    def run(self,mode,drivers_cot=8,thread_cot=8):
        self.thread_pool = ThreadPool(thread_cot)
        if mode==2:
            drivers_cot = 0
        if drivers_cot>0:
            self.drivers_pool = DriversPool(
                visual=False,    size=drivers_cot,
                launch_with_thread_pool=self.thread_pool,
            )
        if mode==1:
            #mode 1 是在第一阶段,rank页journal没有全拿下来之前
            #主要是为了初始化生成条目
            self.thread_pool.map(
                func = self.get_rank_journal_info,
                iterable = self.get_db_category_ids()
            )
        elif mode==2:
            #mode 2 第二阶段，进入详情页拿信息
            #出发点是从阶段一中的条目开始
            self.thread_pool.map(
                func = self.get_detail_journal_info,
                iterable = self.get_db_journal_ids()
            )
        else:
            pass


if __name__=="__main__":
    from src.crawl_tools.WatchDog import close_procs_by_keyword
    close_procs_by_keyword('phantom')
    ge = JournalInfoGenerator()
    #ge.is_crawled_in_rank_page(category_id=3403)
    ge.run(mode=2,drivers_cot=0,thread_cot=32)

