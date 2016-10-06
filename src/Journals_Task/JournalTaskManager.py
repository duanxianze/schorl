#coding:utf-8
"""
@file:      MajorTaskManager.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-18 0:01
@description:
            特定领域下的杂志爬虫任务启动模块，调度数据库和爬虫
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

import random
from Journals_Task.ExistedSpiders import EXISTED_SPIDERS
from Journals_Task.GetDBJournals import MajorEntrance,PublisherEntrance
from multiprocessing.dummy import Pool as ThreadPool
from Journals_Task.JournalClass import Journal
from crawl_tools.DriversPool import DriversPool

class JournalTaskManager:
    def __init__(self,keyword):
        self.keyword = keyword

    def get_journals_info(self,
        EntranceFunc = PublisherEntrance,
        single_area_relation = True,
        index_by_area = False,
        index_by_category = True,
        open_access = True,
        max_count = 100
    ):
        if EntranceFunc==MajorEntrance:
            return MajorEntrance(
                major_keyword = self.keyword
            ).get_possible_journals(
                single_area_relation=single_area_relation,
                index_by_area=index_by_area,
                index_by_category=index_by_category,
                open_access=open_access,
                limit = max_count
            )
        if EntranceFunc==PublisherEntrance:
            return PublisherEntrance(
                publisher_keyword=self.keyword
            ).get_unfinished_journals(
                single_area_relation=single_area_relation,
                open_access=open_access,
                limit = max_count
            )
        return []

    def get_task_spider(self,spiders_infos,journal_url):
        for spider_info in spiders_infos:
            for publisherKeyword in spider_info['publisherKeywords']:
                if publisherKeyword in journal_url:
                    return spider_info['publisherSpiderClass'],spider_info['need_webdriver']
        return None

    def launch_journal_spider(self,db_journal_item):
        JournalObj = Journal()
        JournalObj.name = db_journal_item[0]
        JournalObj.sjr_id = db_journal_item[1]
        JournalObj.site_source = db_journal_item[2]
        JournalObj.area_relation_cot = db_journal_item[3]
        JournalObj.category_relation_cot = db_journal_item[4]
        JournalObj.publisher = db_journal_item[5]
        JournalObj.volume_links_got = db_journal_item[6]
        JournalObj.generate_area_category_id()
        spider_item = self.get_task_spider(EXISTED_SPIDERS,JournalObj.site_source)
        if spider_item:
            Spider = spider_item[0]
            need_webdriver = spider_item[1]
            print('[{}]: Got Task of <{}> ( {} )'.\
                  format(Spider.__name__,JournalObj.name,JournalObj.site_source))
            params = [JournalObj]
            if need_webdriver:
                driverObj = self.drviers_pool.get_one_free_driver()
                params.append(driverObj)
            try:
                Spider(*params).run()
            except Exception as e:
                print('[Error] JournalTaskManager:launch_journal_spider:{}'.format(str(e)))
                return
        else:
            print('[Spider Not Found]: <{}> 所属出版社解析器未找到( {} )'\
                  .format(JournalObj.name,JournalObj.site_source))

    def run(
            self,DB_EntranceFunc,
            journal_need_single_area_relation = True,
            journal_need_open_access = True,
            journal_need_index_by_area = False,
            journal_need_index_by_category = True,
            max_count = 100,
            drvier_is_visual = False,
            thread_cot = 16,
            driver_pool_size = 0
        ):
        journals_info = self.get_journals_info(
            EntranceFunc=DB_EntranceFunc,
            single_area_relation = journal_need_single_area_relation,
            index_by_area = journal_need_index_by_area,
            index_by_category = journal_need_index_by_category,
            open_access = journal_need_open_access,
            max_count = max_count
        )
        thread_pool = ThreadPool(thread_cot)
        self.drviers_pool = DriversPool(
            size = driver_pool_size,
            visual = drvier_is_visual,
            launch_with_thread_pool=thread_pool
        )
        journal_items = []
        for key in journals_info.keys():
            category_name = key
            journal_items.extend(journals_info[key])
            print('\n<%s>: len = %s' % ( category_name,len(journals_info[key])) )
        journal_items = list(set(journal_items))
        random.shuffle(journal_items)
        thread_pool.map(self.launch_journal_spider,journal_items)
        thread_pool.close()
        thread_pool.join()
        raise Exception('fuck you . give me feed ok ???')
