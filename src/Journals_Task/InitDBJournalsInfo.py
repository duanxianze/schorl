#coding:utf-8
"""
@file:      got_journals_info.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-15 14:30
@description:
            获取所有SJRD的journal信息
"""

from src.journal_parser.SJR_Parser import *
from src.crawl_tools.DriversPool import DriversPool
from multiprocessing.dummy import Pool as ThreadPool
from src.db_config import new_db_cursor
import random

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
        print('JournalInfoGenerator:\n\tCategory_id:{}, Journal Amount:{}'.format(category_id,amount))
        cur.close()
        return amount>10

    def is_crawled_in_detail_page(self,journal_sjr_id):
        '''
            判断某杂志社与area的关联表是否已经建过
            搜索category和area的关联表
            若结果数非零则说明已爬（爬过必会有一个或以上）
        '''
        return self.area_relation_cot(journal_sjr_id)>0

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
        #sql = 'select sjr_id from journal WHERE area_relation_cot=0'
        sql = 'select sjr_id from journal WHERE is_crawled=FALSE'
        cur.execute(sql)
        journal_ids = cur.fetchall()
        cur.close()
        return journal_ids

    def area_relation_cot(self,journal_id):
        cur = new_db_cursor()
        cur.execute(
            'select count(*) from journal_area WHERE journal_id={}'.format(journal_id)
        )
        amount = cur.fetchall()[0][0]
        cur.close()
        return amount

    def update_area_relation_cot(self,journal_id):
        amount = self.area_relation_cot(journal_id)
        print(amount,journal_id)
        cur = new_db_cursor()
        cur.execute(
            'update journal set area_relation_cot={} where sjr_id={}'.format(amount,journal_id)
        )
        cur.close()

    def category_relation_cot(self,journal_id):
        cur = new_db_cursor()
        cur.execute(
            'select count(*) from journal_category WHERE journal_id={}'.format(journal_id)
        )
        amount = cur.fetchall()[0][0]
        cur.close()
        return amount

    def update_category_relation_cot(self,journal_id):
        try:
            amount = self.category_relation_cot(journal_id)
            print(amount,journal_id)
            cur = new_db_cursor()
            cur.execute(
                'update journal set category_relation_cot={} where sjr_id={}'.format(amount,journal_id)
            )
            cur.close()
            new_db_cursor().execute(
                    'update journal set is_crawled = true where sjr_id = {}'\
                        .format(journal_id)
                )
            print('update {}ok'.format(journal_id))
        except Exception as e:
            print(str(e))

    def get_detail_journal_info(self,db_item):
        try:
            journal_sjr_id=db_item[0]
            result = JournalDetailPageParser(journal_sjr_id)\
                .save_journal_category()
            if result:
                new_db_cursor().execute(
                    'update journal set is_crawled = true where sjr_id = {}'\
                        .format(journal_sjr_id)
                )
                print('update {}ok'.format(journal_sjr_id))
        except Exception as e:
            print(str(e))
        '''
        self.update_area_relation_cot(journal_sjr_id)
        '''
        '''
        if self.is_crawled_in_detail_page(journal_sjr_id):
            print('[Relations crawled] {}'\
                  .format(journal_sjr_id))
            return
        JournalDetailPageParser(journal_sjr_id)\
            .save_journal_area()
        '''


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
            db_items = self.get_db_category_ids()
            db_items = random.shuffle(db_items)
            self.thread_pool.map(
                func = self.get_rank_journal_info,
                iterable = db_items
            )
        elif mode==2:
            #mode 2 第二阶段，进入详情页拿信息
            #出发点是从阶段一中的条目开始
            self.thread_pool.map(
                func = self.get_detail_journal_info,
                iterable = self.get_db_journal_ids()
            )
        elif mode==3:
            #初始化所有journal的category条目数量
            joutnal_ids = list(map(lambda x:x[0],self.get_db_journal_ids()))
            print(joutnal_ids)
            self.thread_pool.map(
                func = self.update_category_relation_cot,
                iterable = joutnal_ids
            )
        else:
            pass

if __name__=="__main__":
    from src.crawl_tools.WatchDog import close_procs_by_keyword
    close_procs_by_keyword('phantom')
    ge = JournalInfoGenerator()
    #ge.is_crawled_in_rank_page(category_id=3403)
    ge.run(mode=3,drivers_cot=0,thread_cot=32)

